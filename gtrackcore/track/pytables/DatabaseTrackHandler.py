import tables
import os

from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename

class DatabaseTrackHandler(object):
    def __init__(self, track_name, genome, chr, allow_overlaps):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)

        self._h5_filename = getDatabaseFilename(dir_path, track_name)
        self._track_name = track_name
        self._h5_file = None
        self._table = None

    def open(self, mode='r'):
        self._h5_file = tables.open_file(self._h5_filename, mode, title=self._track_name[-1])
        self._table = self._get_track_table()

    def close(self):
        self._h5_file.close()
        self._h5_file = None
        self._table = None

    #TODO: assertion the way to go?
    def get_column_names(self):
        assert self._table is not None
        return self._table.colnames

    #TODO: assertion the way to go?
    def get_column(self, column_name):
        assert self._table is not None

        return self._table.colinstances[column_name]

    #TODO: Ensure that group path exist
    def _get_track_table(self):
        assert self._h5_file is not None

        print self.__class__.__name__, '', self._get_table_path()

        for g in self._h5_file.walk_groups():
            print self.__class__.__name__, g

        return self._h5_file.get_node(self._get_table_path())

    def _get_table_path(self):
        return '/' + '/'.join(self._track_name) + '/' + self._track_name[-1]

    def create_table(self, table_description, expectedrows):
        self._h5_file = tables.open_file(self._h5_filename, mode='w', title=self._track_name[-1])

        group = self._create_groups()
        self._table = self._h5_file.create_table(group, self._track_name[-1], \
                                                table_description, self._track_name[-1], \
                                                expectedrows=expectedrows)
        self._create_indices()

        return self._table

    def _create_groups(self):
        group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

        for track_name_part in self._track_name[1:]:
            group = self._h5_file.create_group(group, track_name_part, track_name_part)
        return group

    def _create_indices(self):
        self._table.cols.start.create_index()
        self._table.cols.end.create_index()