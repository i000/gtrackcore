__author__ = 'skh'


from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.raw_operations.Union import union


from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track_operations.Genome import Genome

class Union(Operator):
    #_TEST = TrackFormatReq(name="points")

    def _call(self, region, tv1, tv2):
        rawTrack1 = RawOperationContent(self._resultGenome, region, tv=tv1)
        rawTrack2 = RawOperationContent(self._resultGenome, region, tv=tv2)

        ret = union(rawTrack1, rawTrack2, self._resultAllowOverlaps)

        if ret is not None:
            assert len(ret) == 4
            return createRawResultTrackView(ret[0], ret[1], ret[2], ret[3],
                                            [rawTrack1, rawTrack2],
                                            self.resultAllowOverlaps)
        else:
            return None

    def _setConfig(self):
        # None changeable properties
        self._numTracks = 2
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False),
             TrackFormatReq(dense=False, allowOverlaps=False)]

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False
        self._resultIsTrack = True
        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirements = self._trackRequirements[0]

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """
        if 'allowOverlap' in kwargs:
            self._allowOverlap = kwargs['allowOverlap']
            self._updateTrackFormat()

        if 'resultAllowOverlap' in kwargs:
            self._resultAllowOverlaps = kwargs['resultAllowOverlap']
            self._updateResultTrackFormat()

    def _updateTrackFormat(self):
        """
        If we enable or disable overlapping tracks as input, we need to
        update the track requirement as well.
        :return: None
        """
        if self._allowOverlap:
            self._trackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True),
                 TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._trackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False),
                 TrackFormatReq(dense=False, allowOverlaps=False)]

    def _updateResultTrackFormat(self):
        """
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        if self._resultAllowOverlaps:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True),
                 TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False),
                 TrackFormatReq(dense=False, allowOverlaps=False)]

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('intersect', help='Find the intersect of two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Intersect')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        trackA = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)
        trackB = createTrackContentFromFile(genome, args.trackB,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Union(trackA, trackB)
