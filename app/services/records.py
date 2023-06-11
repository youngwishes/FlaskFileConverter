from abc import ABC, abstractmethod
from pathlib import Path
import uuid
import os
from typing import Any
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


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

    def generate_filename(self) -> str:
        return uuid.uuid4().hex

    def delete_old_file(self, path: Path) -> None:
        if os.path.exists(path):
            os.remove(path)

    def get_path_with_suffix(self, suffix: str) -> Path:
        return Path.joinpath(self.filepath, self.generate_filename()).with_suffix(suffix)

    def save(self, path: Path) -> None:
        with open(path, 'wb') as f:
            f.write(self.binary_data)

    def convert(self, delete_converted: bool = True) -> Any:
        wav_fullpath = self.get_path_with_suffix(suffix='.wav')
        self.save(wav_fullpath)
        mp3_fullpath = self.get_path_with_suffix(suffix='.mp3')
        try:
            AudioSegment.from_wav(wav_fullpath).export(mp3_fullpath, format='mp3')
        except (CouldntDecodeError, IndexError):
            self.delete_old_file(path=wav_fullpath)
            return
        if delete_converted:
            self.delete_old_file(path=wav_fullpath)

        return MP3(mp3_fullpath=mp3_fullpath)


class MP3:
    def __init__(self, mp3_fullpath: Path) -> None:
        self.__mp3_fullpath = mp3_fullpath

    @property
    def uuid(self) -> str:
        return os.path.split(self.__mp3_fullpath)[-1]

    @property
    def fullpath(self) -> Path:
        return self.__mp3_fullpath
