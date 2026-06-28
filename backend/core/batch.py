import queue
import threading
from typing import List, Callable, Optional
from PIL import Image

from backend.core.processor import ProcessingTask, ProcessingResult, process_image_worker
from backend.core.cache import ImageCache

class BatchProcessor:
    """Handles batch image processing with threading"""
    
    def __init__(self, max_workers: int = 4, use_cache: bool = True):
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.cache = ImageCache() if use_cache else None
        self.is_cancelled = False
        self.current_threads: List[threading.Thread] = []
        self.tasks_queue = queue.Queue()
    
    def process_batch(self, tasks: List[ProcessingTask], 
                      progress_callback: Optional[Callable[[int, int], None]] = None, 
                      result_callback: Optional[Callable[[ProcessingResult], None]] = None):
        """Process batch of images"""
        self.is_cancelled = False
        
        # Clear previous tasks if any
        while not self.tasks_queue.empty():
            try:
                self.tasks_queue.get_nowait()
            except queue.Empty:
                break
        
        # Add tasks to queue
        for task in tasks:
            self.tasks_queue.put(task)
        
        # Create worker threads
        threads = []
        num_workers = min(self.max_workers, len(tasks))
        if num_workers < 1:
            num_workers = 1
            
        for _ in range(num_workers):
            thread = threading.Thread(target=self._worker, 
                                    args=(progress_callback, result_callback))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        self.current_threads = threads
        
        # Wait for completion
        for thread in threads:
            thread.join()
    
    def _worker(self, progress_callback=None, result_callback=None):
        """Worker thread function"""
        while not self.is_cancelled:
            try:
                task = self.tasks_queue.get(timeout=0.1)
            except queue.Empty:
                break
            
            # Check cache
            cached_result = None
            if self.use_cache and self.cache:
                cached_img = self.cache.get(task.file_path, task.settings)
                if cached_img:
                    # Use cached image
                    try:
                        output_format = task.settings.get('output_format', 'jpg')
                        output_path = task.output_path.with_suffix(f'.{output_format}')
                        
                        save_kwargs = {'quality': task.settings.get('quality', 85), 'optimize': True}
                        if output_format == 'jpg':
                            save_kwargs['format'] = 'JPEG'
                        elif output_format == 'webp':
                            save_kwargs['format'] = 'WEBP'
                        elif output_format == 'png':
                            save_kwargs['format'] = 'PNG'
                        
                        # Ensure output directory exists
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        cached_img.save(output_path, **save_kwargs)
                        
                        original_size = task.file_path.stat().st_size
                        new_size = output_path.stat().st_size
                        
                        cached_result = ProcessingResult(
                            success=True,
                            file_path=task.file_path,
                            output_path=output_path,
                            error=None,
                            original_size=original_size,
                            new_size=new_size,
                            compression_ratio=((original_size - new_size) / original_size * 100) if original_size > 0 else 0,
                            processing_time=0.01
                        )
                    except Exception as e:
                        cached_result = None
            
            # Process image
            if cached_result:
                result = cached_result
            else:
                result = process_image_worker(task)
                
                # Cache successful result
                if result.success and self.use_cache and self.cache and result.output_path:
                    try:
                        with Image.open(result.output_path) as img:
                            self.cache.put(task.file_path, task.settings, img)
                    except:
                        pass
            
            # Callbacks
            if progress_callback:
                progress_callback(task.index, task.total)
            
            if result_callback:
                result_callback(result)
            
            self.tasks_queue.task_done()
    
    def cancel(self):
        """Cancel processing"""
        self.is_cancelled = True
        
        # Clear queue
        while not self.tasks_queue.empty():
            try:
                self.tasks_queue.get_nowait()
                self.tasks_queue.task_done()
            except queue.Empty:
                break
