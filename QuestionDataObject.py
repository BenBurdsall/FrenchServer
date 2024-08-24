import json

class questionDataObject:
    def __init__(self):
        self.workingSet = []
        self.repeatBatch = 1
        self.batchSize = 30
        self.noBatchRepeats = 3
        self.repeatBatchCount = self.noBatchRepeats
        self.workingBatch = []
        self.wordsInBatch = 0
        self.batch = []

    def to_dict(self):
        return {
            'workingSet': json.dumps(self.workingSet),
            'repeatBatch': self.repeatBatch,
            'batchSize': self.batchSize,
            'noBatchRepeats': self.noBatchRepeats,
            'repeatBatchCount': self.repeatBatchCount,
            'workingBatch': json.dumps(self.workingBatch),
            'wordsInBatch': self.wordsInBatch,
            'batch': json.dumps(self.batch)
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.workingSet = json.loads(data.get('workingSet', '[]'))
        obj.repeatBatch = data.get('repeatBatch', 1)
        obj.batchSize = data.get('batchSize', 30)
        obj.noBatchRepeats = data.get('noBatchRepeats', 3)
        obj.repeatBatchCount = data.get('repeatBatchCount', obj.noBatchRepeats)
        obj.workingBatch = json.loads(data.get('workingBatch', '[]'))
        obj.wordsInBatch = data.get('wordsInBatch', 0)
        obj.batch = json.loads(data.get('batch', '[]'))
        return obj
