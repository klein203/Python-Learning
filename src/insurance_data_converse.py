'''
@author: xusheng
'''

from multiprocessing import Process, Queue
import os, time, random
import xlrd
import xlwt
from six.moves import xrange
import argparse

class DataObject(object):
    @property
    def order_date(self):
        return self._order_date
        
    @order_date.setter
    def order_date(self, value):
        self._order_date = value
    
    @property
    def insurance_name(self):
        return self._insurance_name
        
    @insurance_name.setter
    def insurance_name(self, value):
        self._insurance_name = value
    
    @property
    def insurance_type(self):
        return self._insurance_type
        
    @insurance_type.setter
    def insurance_type(self, value):
        self._insurance_type = value

    @property
    def insurance_premium(self):
        return self._insurance_premium
        
    @insurance_premium.setter
    def insurance_premium(self, value):
        self._insurance_premium = value

    @property
    def insurance_commission(self):
        return self._insurance_commission
        
    @insurance_commission.setter
    def insurance_commission(self, value):
        self._insurance_commission = value
    
    @property
    def staff_no(self):
        return self._staff_no
        
    @staff_no.setter
    def staff_no(self, value):
        self._staff_no = value

class VProcess(Process):
    def __init__(self, name, queue, path):
        Process.__init__(self, name=name)
        self._queue = queue
        self._path = path

class QueueWriteProcess(VProcess):
    def _preprocess_date(self, ctype, value):
        # ctype: 0 empty, 1 string, 2 number, 3 date, 4 boolean, 5 error
        val = value
        if ctype == 0:
            pass
        elif ctype == 1:
            val = val.replace('\.','\-')
        elif ctype == 2:
            pass
        elif ctype == 3:
            val = xlrd.xldate.xldate_as_datetime(val, 0)
            val = val.strftime("%Y-%m-%d")
        elif ctype == 4:
            pass
        else:
            pass
        
        return val
        
    def run(self):
        print('[->|  ] PID [%s]: %s is running...' % (os.getpid(), self.name))
        titleIncluded = 1
        
        # TODO: load file list
        filelist = os.listdir(self._path)
#         filelist = [f for f in os.listdir(os.path.join('..', 'data', 'insurance', 'raw')) if f.endswith(".xls") or f.endswith(".xlst")]
        for file in filelist:
            workbook = xlrd.open_workbook(os.path.join(self._path, file))
            print('[->|  ] Workbook [%s] Begin' % (file))
            sheets = workbook.sheets()
            for sheet in sheets:
                nrows = sheet.nrows
                print('[->|  ] Sheet [%s].[%s], Rows [%d] Begin' % (file, sheet.name, (nrows + 1 - titleIncluded)))
                # insurance_type, insurance_name, order_date, insurance_premium, insurance_commission, staff_no
                offsets = [1, 2, 7, 14, 15, 18]
                for row in xrange(nrows):
                    if row < titleIncluded:
                        continue
            
                    obj = DataObject()
                    obj.insurance_type = sheet.cell_value(row, offsets[0])
                    obj.insurance_name = sheet.cell_value(row, offsets[1])
                    obj.order_date = self._preprocess_date(sheet.cell(row, offsets[2]).ctype, sheet.cell_value(row, offsets[2]))
                    obj.insurance_premium = sheet.cell_value(row, offsets[3])
                    obj.insurance_commission = sheet.cell_value(row, offsets[4])
                    obj.staff_no = sheet.cell_value(row, offsets[5])
#                     print(obj)
                    self._queue.put(obj)
                    time.sleep(random.random() / 10)
                print('[->|  ] Sheet [%s].[%s], Rows [%d] End' % (file, sheet.name, (nrows + 1 - titleIncluded)))
            print('[->|  ] Workbook [%s] End' % (file))

class QueueReadProcess(VProcess):
    def run(self):
        time.sleep(2)
        dst_name = '车享家保单.xls'
        print('[  |->] PID [%s]: %s is running...' % (os.getpid(), self.name))
        
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
        header, shape = self._init_header()
        row_cnt = 0
        
        for row in xrange(shape[0]):
            for col in xrange(shape[1]):
                sheet.write(row_cnt, col, label=header[row][col])
            row_cnt += 1
        
        while not self._queue.empty():
            obj = self._queue.get(True)
#             print('Get from queue [%s, %s, %s, %s]' % (obj.insurance_name, obj.insurance_type, obj.insurance_premium, obj.insurance_commission))
            
            sheet.write(row_cnt, 0, label=obj.order_date)
            sheet.write(row_cnt, 1, label=obj.insurance_name)
            sheet.write(row_cnt, 2, label=obj.insurance_type)
            sheet.write(row_cnt, 3, label=obj.insurance_premium)
            sheet.write(row_cnt, 4, label=obj.insurance_commission)
            sheet.write(row_cnt, 5, label=obj.staff_no)
            
            print('[  |->] Task Done [%d], Task Queued [%d]' % ((row_cnt + 1 - shape[0]), self._queue.qsize()))
            row_cnt += 1
            time.sleep(random.random() / 5)
        
        print('[  |->] Saving excel file [%s] to disk ...' % os.path.join(self._path, dst_name))
        workbook.save(os.path.join(self._path, dst_name))
        print('[  |->] Excel file [%s] saved' % os.path.join(self._path, dst_name))

    def _init_header(self):
        headers = [['col1', 'col2', 'col3', 'col4', 'col5', 'col6'],
                   ['varchar2', 'varchar2', 'varchar2', 'varchar2', 'varchar2', 'varchar2'],
                   ['2018-06-05', 'demo', '商业', 'demo', 'demo', 'demo'],
                   ['签单日期', '保险公司名称', '险种', '含税保费', '手续费金额', '员工工号']
            ]
        return headers, (len(headers), len(headers[0]))

class BatchProcessManager(object):
    def __init__(self, from_path, to_path):
        self._queue = Queue()
        self._writer = QueueWriteProcess('Writer', self._queue, from_path)
        self._reader = QueueReadProcess('Reader', self._queue, to_path)
    
    def run(self):
        self._writer.start()
        self._reader.start()
    
        self._writer.join()
        self._reader.join()

        
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Insurance Data Process Helper:  Usage: python <command.py> [--src SOURCE_PATH] [--dst DEST_PATH]')
    parser.add_argument('--src', type=str, default=os.path.join('.', 'src'), dest='src', help='source file path')
    parser.add_argument('--dst', type=str, default=os.path.join('.', 'dst'), dest='dst', help='target file path')
    args = parser.parse_args()
    
#     os.makedirs(args.dst)
    
    manager = BatchProcessManager(args.src, args.dst)
    manager.run()