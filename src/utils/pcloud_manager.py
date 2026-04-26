import requests
import io
from pypdf import PdfReader
from config import Config

class PCloudManager:
    @staticmethod
    def fetch_notes(pcloud_url: str) -> str:
        if not pcloud_url:
            return ""

        try:
            code = pcloud_url.split("code=")[-1]
            # Tenta Europa primeiro
            api_base = Config.PCLOUD_API_URL
            response = requests.get(f"{api_base}/showpublink", params={"code": code})
            data = response.json()

            if data.get("result") != 0:
                api_base = Config.PCLOUD_GLOBAL_URL
                response = requests.get(f"{api_base}/showpublink", params={"code": code})
                data = response.json()

            if data.get("result") == 0:
                pdf_files = [item for item in data['metadata'].get('contents', []) if item.get("name", "").endswith(".pdf")]
                all_text = ""
                for pdf in pdf_files:
                    dl_res = requests.get(f"{api_base}/getpublinkdownload", params={"code": code, "fileid": pdf['fileid']})
                    dl_data = dl_res.json()
                    if dl_data.get("result") == 0:
                        host = dl_data['hosts'][0]
                        file_res = requests.get(f"https://{host}{dl_data['path']}")
                        reader = PdfReader(io.BytesIO(file_res.content))
                        for page in reader.pages:
                            all_text += page.extract_text() + "\n"
                return all_text
        except Exception as e:
            print(f"PCloud Error: {e}")
            return ""
        return ""
