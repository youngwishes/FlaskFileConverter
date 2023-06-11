from abc import ABC, abstractmethod
from pathlib import Path
import uuid
import os
from pydub import AudioSegment


class AbstractMediaService(ABC):
    def __init__(self, binary_data: bytes, filepath: Path) -> None:
        self.binary_data = binary_data
        self.filepath = filepath

    @abstractmethod
    def generate_filename(self):
        pass

    def get_path_with_suffix(self, suffix: str):
        pass

    @abstractmethod
    def delete_old_file(self, path: Path):
        pass


class RecordService(AbstractMediaService):

    def generate_filename(self):
        return uuid.uuid4().hex

    def delete_old_file(self, path: Path):
        if os.path.exists(path):
            os.remove(path)

    def get_path_with_suffix(self, suffix: str):
        return Path.joinpath(self.filepath, self.generate_filename()).with_suffix(suffix)

    def save(self, path: Path):
        with open(path, 'wb') as f:
            f.write(self.binary_data)

    def convert(self, delete_converted: bool = True):
        wav_fullpath = self.get_path_with_suffix(suffix='.wav')
        self.save(wav_fullpath)
        mp3_fullpath = self.get_path_with_suffix(suffix='.mp3')
        AudioSegment.from_wav(wav_fullpath).export(mp3_fullpath, format='mp3')
        if delete_converted:
            self.delete_old_file(path=wav_fullpath)
        return os.path.split(mp3_fullpath)[-1]
