'''
@author: xusheng
'''

import xlrd
import xlwt
from six.moves import xrange

class Service(object):
    @ property
    def partner_id(self):
        return self._partner_id
    
    @ partner_id.setter
    def partner_id(self, value):
        self._partner_id = value
    
    @ property
    def partner_name(self):
        return self._partner_name
    
    @ partner_name.setter
    def partner_name(self, value):
        self._partner_name = value
    
    @ property
    def order_by(self):
        return self._order_by
    
    @ order_by.setter
    def order_by(self, value):
        self._order_by = value
        
    @ property
    def service_type(self):
        return self._service_type
    
    @ service_type.setter
    def service_type(self, value):
        self._service_type = value
    
    @ property
    def service_name(self):
        return self._service_name
    
    @ service_name.setter
    def service_name(self, value):
        self._service_name = value
        
    @ property
    def service_desc(self):
        return self._service_desc
    
    @ service_desc.setter
    def service_desc(self, value):
        self._service_desc = value
    
    @ property
    def service_msrp(self):
        return self._service_msrp
    
    @ service_msrp.setter
    def service_msrp(self, value):
        self._service_msrp = value
        
    @ property
    def service_price(self):
        return self._service_price
    
    @ service_price.setter
    def service_price(self, value):
        self._service_price = value
    
    @ property
    def service_excode(self):
        return self._service_excode
    
    @ service_excode.setter
    def service_excode(self, value):
        self._service_excode = value
        
    @ property
    def appointment_support(self):
        return self._appointment_support
    
    @ appointment_support.setter
    def appointment_support(self, value):
        self._appointment_support = value
                
    @ property
    def appointment_desc(self):
        return self._appointment_desc
    
    @ appointment_desc.setter
    def appointment_desc(self, value):
        self._appointment_desc = value

def load_services_template(sheet, titleIncluded=2):
    services_template = {}
    nrows = sheet.nrows
    for row in xrange(nrows):
        if row < titleIncluded:
            continue
            
        service_info = Service()
        service_info.partner_id = sheet.cell_value(row, 0)
        service_info.partner_name = sheet.cell_value(row, 1)
        service_info.order_by = sheet.cell_value(row, 2)
        service_info.service_type = sheet.cell_value(row, 3)
        service_info.service_name = sheet.cell_value(row, 4)
        service_info.service_desc = sheet.cell_value(row, 5)
        service_info.service_msrp = sheet.cell_value(row, 6)
        service_info.service_price = sheet.cell_value(row, 7)
        service_info.service_excode = sheet.cell_value(row, 8)
        service_info.appointment_support = sheet.cell_value(row, 9)
        service_info.appointment_desc = sheet.cell_value(row, 10)
        services_template[service_info.partner_id] = service_info
    return services_template

def write_service_line(sheet, i, j, service_line):
    sheet.write(i, j+0, label=service_line.partner_id)
    sheet.write(i, j+1, label=service_line.partner_name)
    sheet.write(i, j+2, label=service_line.order_by)
    sheet.write(i, j+3, label=service_line.service_type)
    sheet.write(i, j+4, label=service_line.service_name)
    sheet.write(i, j+5, label=service_line.service_desc)
    sheet.write(i, j+6, label=service_line.service_msrp)
    sheet.write(i, j+7, label=service_line.service_price)
    sheet.write(i, j+8, label=service_line.service_excode)
    sheet.write(i, j+9, label=service_line.appointment_support)
    sheet.write(i, j+10, label=service_line.appointment_desc)

def step_count(m):
    i = 0
    while i < m:
        yield(i)
        i += 1

if __name__ == '__main__':
    step = step_count(100000)
    
    wb_services = xlrd.open_workbook('ETCP.xlsx')
    sh_services_ref = wb_services.sheets()[0]
    services_template = load_services_template(sh_services_ref)
    
    sh_matrix = wb_services.sheets()[1]
    nrows = sh_matrix.nrows
    ncols = sh_matrix.ncols
    
    wb_result = xlwt.Workbook(encoding = 'utf-8')
    sh_result = wb_result.add_sheet('result', cell_overwrite_ok=True)
    
    # data converse
    for i in xrange(nrows):
        # skip first 2 rows (title)
        if i < 2:
            continue
         
        partner_name = sh_matrix.cell_value(i, 0)
         
        for j in xrange(1, ncols):
            # skip null cell
            if sh_matrix.cell(i, j).ctype == 0:
#                 print("(%d, %d) is null" % (i, j))
                continue
             
            idx = sh_matrix.cell_value(1, j)
            price = sh_matrix.cell_value(i, j)
#             print("%s -> %s" % (idx, price))
             
            service_template = services_template[idx]
             
            service_line = Service()
            service_line.partner_id = service_template.partner_id
            service_line.partner_name = partner_name
            service_line.order_by = service_template.order_by
            service_line.service_type = service_template.service_type
            service_line.service_name = service_template.service_name
            service_line.service_desc = service_template.service_desc
            if idx in ('A', 'B', 'C'):
                service_line.service_msrp = price
            else:
                service_line.service_msrp = service_template.service_msrp
            service_line.service_price = price
            service_line.service_excode = service_template.service_excode
            service_line.appointment_support = service_template.appointment_support
            service_line.appointment_desc = service_template.appointment_desc
     
            write_service_line(sh_result, next(step), 0, service_line)
             
    wb_result.save('ETCP_res.xls')
