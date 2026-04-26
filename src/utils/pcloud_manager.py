import requests
import io
from pypdf import PdfReader
from config import Config

class PCloudManager:
    @staticmethod
    def fetch_notes(url: str) -> str:
        """Fetch PDF content from either pCloud public link or direct URL."""
        if not url:
            return ""

        # Check if it's a pCloud URL or direct URL
        if "pcloud.com" in url or "code=" in url:
            return PCloudManager._fetch_from_pcloud(url)
        else:
            return PCloudManager._fetch_from_direct_url(url)

    @staticmethod
    def _fetch_from_pcloud(pcloud_url: str) -> str:
        """Fetch PDFs from pCloud public link."""
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
                            text = page.extract_text()
                            if text:
                                all_text += text + "\n"
                return all_text
        except Exception as e:
            print(f"PCloud Error: {e}")
            return ""
        return ""

    @staticmethod
    def _fetch_from_direct_url(direct_url: str) -> str:
        """Fetch PDF from direct file URL (supports multiple formats)."""
        try:
            # Try to download the file
            response = requests.get(direct_url, timeout=10)
            response.raise_for_status()

            # Check if it's a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not direct_url.lower().endswith('.pdf'):
                print(f"Warning: URL doesn't appear to be a PDF (content-type: {content_type})")

            # Try to extract text from PDF
            try:
                reader = PdfReader(io.BytesIO(response.content))
                all_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
                return all_text
            except Exception as pdf_err:
                print(f"Error parsing PDF from direct URL: {pdf_err}")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"Direct URL Error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error fetching from direct URL: {e}")
            return ""
