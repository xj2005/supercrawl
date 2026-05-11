import os
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

class ImageDownloader:
    def __init__(self, save_dir="../output/images", max_workers=5):
        self.save_dir = save_dir
        self.max_workers = max_workers
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def _download_single(self, task):
        """下载单张图片的任务逻辑"""
        url, title = task
        # 处理 Windows 文件名不能包含的特殊字符
        safe_title = "".join([c for c in title if c not in r'\/:*?"<>|'])
        file_path = os.path.join(self.save_dir, f"{safe_title}.jpg")

        # 断点续传逻辑：如果文件已存在，直接跳过
        if os.path.exists(file_path):
            logging.info(f"图片已存在，跳过下载: {safe_title}.jpg")
            return

        try:
            # 简单的请求，图片一般反爬不严
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logging.info(f"海报下载成功: {safe_title}.jpg")
            else:
                logging.warning(f"下载失败 {safe_title}: 状态码 {response.status_code}")
        except Exception as e:
            logging.error(f"图片下载异常 {safe_title}: {e}")

    def download_batch(self, image_tasks):
        """
        多线程批量下载海报
        :param image_tasks: 列表，格式为 [(url1, title1), (url2, title2)]
        """
        logging.info("开始多线程下载海报...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self._download_single, image_tasks)
        logging.info("本批次海报下载任务完成。")