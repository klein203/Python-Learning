'''
@author: xusheng
'''

import os
import xlwt
from six.moves import xrange
import argparse

class Sequence(object):
    def __init__(self, sequence, **kwargs):
        self._sequence = sequence
        self._trunc_head = 0
        self._trunc_tail = 1
        
        if 'trunc_head' in kwargs:
            self._trunc_head = int(kwargs['trunc_head'])
            
        if 'trunc_tail' in kwargs:
            self._trunc_tail = int(kwargs['trunc_tail'])
        
        self._trunc_sequence = sequence[self._trunc_head:-self._trunc_tail]
    
    @property
    def sequence(self):
        return self._sequence

    @property
    def trunc_sequence(self):
        return self._trunc_sequence

class SSA():
    def __init__(self):
        self._init_ref_sequence()
        self._logger = SSARecordLogger()
    
    def _init_ref_sequence(self):
        self._ref_seq = Sequence(self._load_seq(FLAGS.ref))
    
    def _load_sample_sequence(self, file):
        d_trunc = {'trunc_head': FLAGS.trunc_head, 'trunc_tail': FLAGS.trunc_tail}
        return Sequence(self._load_seq(file), **d_trunc)
    
    def _load_seq(self, file):
        seq = ''
        with open(file, 'r') as f:
            l = f.readline()
            seq += l
        return seq
    
    def _check(self, ref_sequence, sample_sequence):
#         print('SAMPLE(%d): %s' % (len(sample_sequence.trunc_sequence), sample_sequence.trunc_sequence))
        return (sample_sequence.trunc_sequence in ref_sequence.sequence)
    
    def process(self):
        filelist = os.listdir(FLAGS.src)
        
        for file in filelist:
            idx = file.index('-')
            patient_no = file[0:idx]
            sample_sequence = self._load_sample_sequence(os.path.join(FLAGS.src, file))
            b_check = self._check(self._ref_seq, sample_sequence)
            
            if b_check:
                d_record = {
                    'reaction': FLAGS.reaction,
                    'patient_no': patient_no,
                    'result': 'MATCH'
                }
            else:
                d_record = {
                    'reaction': FLAGS.reaction,
                    'patient_no': patient_no,
                    'result': 'ERROR',
                    'memo': sample_sequence.trunc_sequence
                }
            
            self._logger.log(SSARecord(**d_record))
        
        self._logger.flush()
            

class SSARecord(object):
    def __init__(self, **kwargs):
        self._items = {
            'reaction': '',
            'patient_no': '' ,
            'result': '',
            'memo': ''
        }
        
        for kwarg in kwargs:
            if kwarg not in self._items:
                raise TypeError('Keyword argument not understood:', kwarg)
            self._items[kwarg] = kwargs[kwarg]
        
    @property
    def items(self):
        return self._items

class Logger(object):
    def __init__(self):
        self._init_logger()
    
    def _init_logger(self):
        pass
    
    def log(self, obj):
        if isinstance(obj, str):
            print(obj)
    
    def flush(self):
        pass

class SSARecordLogger(Logger):
    def _init_logger(self):
        self._workbook = xlwt.Workbook(encoding='utf-8')
        self._sheet = self._workbook.add_sheet('sheet1', cell_overwrite_ok=True)
        
        self._cursor = 0
        self._init_header(self._sheet)
    
    def _init_header(self, sheet):
        header, shape = self._header_info()
        for row in xrange(shape[0]):
            for col in xrange(shape[1]):
                sheet.write(self._cursor, col, label=header[row][col])
            self._cursor += 1
    
    def log(self, obj):
        if isinstance(obj, SSARecord):
            self._sheet.write(self._cursor, 0, label=obj.items['reaction'])
            self._sheet.write(self._cursor, 1, label=obj.items['patient_no'])
            self._sheet.write(self._cursor, 2, label=obj.items['result'])
            self._sheet.write(self._cursor, 3, label=obj.items['memo'])
            self._cursor += 1
        else:
            pass
    
    def flush(self):
        self._workbook.save(FLAGS.log)
        
    def _header_info(self):
        headers = [['Reaction', 'Patient_No', 'Result', 'Memo'],]
        return headers, (len(headers), len(headers[0]))

if __name__=='__main__':
    global FLAGS
    parser = argparse.ArgumentParser(description='Sanger Sequencing Analysis Toolkit Helper:')
    parser.add_argument('--ref', dest='ref', type=str, default=os.path.join('.', 'ref'), help='reference file')
    parser.add_argument('--src', dest='src', type=str, default=os.path.join('.', 'src'), help='source file path')
#     parser.add_argument('--tar', dest='tar', type=str, default=os.path.join('.', 'tar'), help='target file path')
    parser.add_argument('--log', dest='log', type=str, default=os.path.join('.', 'log'), help='log file with XLS format')
    parser.add_argument('--trunc_head', dest='trunc_head', type=int, default=30, help='numbers for head truncation')
    parser.add_argument('--trunc_tail', dest='trunc_tail', type=int, default=10, help='numbers for tail truncation')
    parser.add_argument('--reaction', dest='reaction', type=str, default='UNDEFINED', help='reaction category')
    
    FLAGS = parser.parse_args()

    ssa = SSA()
    ssa.process()
