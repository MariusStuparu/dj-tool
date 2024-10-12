"""
This module is responsible for processing the playlist file.
"""


class TextProcessingException(Exception):
    pass


class PlaylistFileProcessing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tracks = []

    def read_file(self):
        with open(file=self.file_path, mode='r') as f:
            lines = f.readlines()

            try:
                line = 0
                while line < len(lines):
                    if lines[line].startswith('#EXTVDJ'):
                        data = lines[line].replace('#EXTVDJ:', '').replace('\n', '')
                        track_data = self.extract_xml_data(data)
                        self.tracks.append({
                            'track_name': track_data,
                            'track_file': lines[line+1]
                        })
                        line += 2
                        continue
                    elif lines[line].startswith('#EXTINF'):
                        data = lines[line].replace('#EXTINF:', '').replace('\n', '')
                        track_data = self.extract_track_data(data)
                        self.tracks.append({
                            **track_data,
                            'track_file': lines[line + 1]
                        })
                        line += 2
                        continue
                    else:
                        line += 1
            except IndexError as idx_err:
                raise TextProcessingException(f'IndexError: The playlist file is not formatted correctly.\n${idx_err}')

    @staticmethod
    def extract_xml_data(text) -> dict:
        """
        Extracts the XML data from the text.
        param text: The text to extract the XML data from.
        :return: The XML data as a dictionary.
        """
        extraxted_data = {}

        return extraxted_data

    @staticmethod
    def extract_track_data(incoming_text) -> dict:
        """
        Extracts the track data from the text.
        param incoming_text: The text to extract the track data from.
        :return: The track data as a dictionary.
        """
        extracted_data = {}
        split_string = incoming_text.split(',')

        for chunk in split_string:
            if not chunk.isnumeric():
                extracted_data['track_name'] = chunk

        return extracted_data


if __name__ == '__main__':
    pass
