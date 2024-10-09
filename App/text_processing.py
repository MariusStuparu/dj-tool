"""
This module is responsible for processing the playlist file.
"""


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
                        data = lines[line].replace('#EXTVDJ:', '')
                        track_data = self.extract_xml_data(data)
                        self.tracks.append({
                            'track_name': track_data,
                            'track_file': lines[line+1]
                        })
                        continue
                    elif lines[line].startswith('#EXTINF'):
                        data = lines[line].replace('#EXTINF:', '')
                        track_data = self.extract_track_data(data)
                        self.tracks.append({
                            'track_name': track_data,
                            'track_file': lines[line + 1]
                        })
                        continue
                    else:
                        line += 1
            except IndexError:
                pass

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
    def extract_track_data(text) -> dict:
        """
        Extracts the track data from the text.
        param text: The text to extract the track data from.
        :return: The track data as a dictionary.
        """
        extracted_data = {}

        return extracted_data


if __name__ == '__main__':
    pass
