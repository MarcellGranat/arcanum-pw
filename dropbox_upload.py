import dropbox
import os
from dropbox.files import WriteMode
import dotenv
from tqdm import tqdm

dotenv.load_dotenv(".venv/.env")

access_token = os.environ['dropbox']

class DropboxUpload:
    def __init__(self, access_token):
        self.access_token = access_token
        self.dbx = dropbox.Dropbox(self.access_token)

    def upload_file(self, file_from, file_to):
        with open(file_from, 'rb') as f:
            self.dbx.files_upload(f.read(), file_to.replace("data", "arcanum_pw"))

    def upload_folder(self, folder_from, folder_to):
        skipped_files = 0

        for root, dirs, files in tqdm(os.walk(folder_from)):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, folder_from)
                dropbox_path = os.path.join(folder_to, relative_path).replace("\\", "/")

                try:
                    self.dbx.files_get_metadata(dropbox_path)
                    skipped_files += 1
                except dropbox.exceptions.ApiError as err:
                    if err.error.is_path() and err.error.get_path().is_not_found():
                        with open(local_path, 'rb') as f:
                            self.dbx.files_upload(f.read(), dropbox_path, mode=WriteMode('overwrite'))
                            if skipped_files > 0:
                                print(f"Skipped {skipped_files} files")
                                skipped_files = 0
                            print(f"Uploaded {dropbox_path}")
                    else:
                        print(f"Failed to check existence of {dropbox_path}: {err}")

if __name__ == '__main__':
    dbx = DropboxUpload(access_token)
    dbx.upload_folder("data", "/arcanum_pw")