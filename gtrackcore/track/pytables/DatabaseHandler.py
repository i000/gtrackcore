import tables
from tables.group import NoSuchNodeError

from gtrackcore.util.CustomExceptions import DBNotOpenError
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename
from abc import ABCMeta, abstractmethod

class DatabaseHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        self._h5_filename = getDatabaseFilename(dir_path, track_name)
        self._track_name = track_name
        self._h5_file = None
        self._table = None

    @abstractmethod
    def open(self, mode='r'):
        self._h5_file = tables.open_file(self._h5_filename, mode=mode, title=self._track_name[-1])

    def close(self):
        self._h5_file.close()
        self._h5_file = None
        self._table = None

    def _get_table_path(self):
        return '/%s/%s' % ('/'.join(self._track_name), self._track_name[-1])


class DatabaseReadHandler(DatabaseHandler):

    def __init__(self, track_name, genome, allow_overlaps):
        super(DatabaseReadHandler, self).__init__(track_name, genome, allow_overlaps)

    def get_column(self, column_name):
        try:
            return self._table.colinstances[column_name]
        except AttributeError:
            raise DBNotOpenError()

    def get_column_names(self):
        try:
            return self._table.colnames
        except AttributeError:
            raise DBNotOpenError()

    def open(self):
        super(DatabaseReadHandler, self).open('r')
        self._table = self._get_track_table()

    def _get_track_table(self):
        try:
            return self._h5_file.get_node(self._get_table_path())
        except AttributeError:
            raise DBNotOpenError()


class TrackCreationDatabaseHandler(DatabaseHandler):

    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackCreationDatabaseHandler, self).__init__(track_name, genome, allow_overlaps)
        self._flush_counter = 0

    def create_table(self, table_description, expectedrows):
        group = self._create_groups()

        try:
            self._table = self._h5_file.create_table(group, self._track_name[-1], \
                                                     table_description, self._track_name[-1], \
                                                     expectedrows=expectedrows)
            self._create_indices()
        except AttributeError:
            raise DBNotOpenError()

    def get_row(self):
        return self._table.row

    def open(self):
        super(TrackCreationDatabaseHandler, self).open('w')

    def flush(self):
        self._flush_counter += 1

        from gtrackcore.util.DatabaseConstants import FLUSH_LIMIT
        try:
            if self._flush_counter == FLUSH_LIMIT:
                self._table.flush()
                self._flush_counter = 0
        except AttributeError:
            raise DBNotOpenError

    def _create_groups(self):
        group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

        for track_name_part in self._track_name[1:]:
            group = self._h5_file.create_group(group, track_name_part, track_name_part)

        return group

    def _create_indices(self):
        self._table.cols.start.create_index()
        self._table.cols.end.create_index()


class BoundingRegionCreationDatabaseHandler(DatabaseHandler):

    def __init__(self, track_name, genome, allow_overlaps):
        super(BoundingRegionCreationDatabaseHandler, self).__init__(track_name, genome, allow_overlaps)

    def create_table(self, table_description, expectedrows):
        group = self._create_groups()

        try:
            self._table = self._h5_file.create_table(group, 'bounding_regions',
                                                     table_description, 'bounding_regions',
                                                     expectedrows=expectedrows)
            self._create_indices()
        except AttributeError:
            raise DBNotOpenError()

    def get_row(self):
        return self._table.row

    def open(self):
        super(BoundingRegionCreationDatabaseHandler, self).open('w')

    def _create_groups(self):
        group = self._get_track_group()
        if group is None:
            group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

            for track_name_part in self._track_name[1:]:
                group = self._h5_file.create_group(group, track_name_part, track_name_part)

        return group

    def _get_track_group(self):
        try:
            return self._h5_file.get_node(self._get_track_group_path())
        except tables.group.NoSuchNodeError:
            return None

    def _get_track_group_path(self):
        return '/%s' % ('/'.join(self._track_name))

    def _create_indices(self):
        pass


