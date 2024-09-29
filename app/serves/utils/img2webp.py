import hashlib
import os
import shutil
import requests
from PIL import Image


class ImageProcessor:
    def __init__(self, outdir: str):
        self.outdir = outdir
        self.images_dir = os.path.join(outdir, 'images')
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

    def save_uri_image(self, uri: str):
        """Save image URI to local directory.

        If it fails, return None.
        """
        md5 = hashlib.md5()
        md5.update(uri.encode('utf8'))
        uuid = md5.hexdigest()[0:6]
        filename = uuid + uri[uri.rfind('.'):]
        image_path = os.path.join(self.images_dir, filename)

        print(f'Downloading {uri}')
        try:
            if uri.startswith('http'):
                resp = requests.get(uri, stream=True)
                if resp.status_code == 200:
                    with open(image_path, 'wb') as image_file:
                        for chunk in resp.iter_content(1024):
                            image_file.write(chunk)
                else:
                    return None, None
            else:
                shutil.copy(uri, image_path)
        except Exception as e:
            print(e)
            return None, None
        return uuid, image_path

    def image2local_webp(self, uri: str):
        """
        Convert image or GIF to WebP format and save to specified output directory.

        :param uri: Input image or GIF file URI.
        :return: Path of the saved WebP file.
        """
        if uri.startswith('http') or not os.path.exists(uri):
            uuid, local_path = self.save_uri_image(uri)
        else:
            local_path = uri

        if not local_path:
            return None

        try:
            with Image.open(local_path) as img:
                base_name = os.path.basename(local_path)
                file_name, _ = os.path.splitext(base_name)
                output_path = os.path.join(self.outdir, f"{file_name}.webp")

                if img.format == 'GIF':
                    img.save(output_path, format='WEBP', save_all=True)
                else:
                    img = img.convert('RGB')
                    img.save(output_path, format='WEBP')

                return output_path
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    input_image_uri = '/home/ke/桌面/my/RAG_project/U-PG-RAG/app/serves/utils/Screenshot-6.png'
    output_directory = './output'
    processor = ImageProcessor(output_directory)
    output_image_path = processor.image2local_webp(input_image_uri)
    print(f"Converted image saved at: {output_image_path}")
