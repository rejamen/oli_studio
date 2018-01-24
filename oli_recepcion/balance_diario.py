# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _

from datetime import datetime,date
from datetime import timedelta
import time
from time import strftime




class balance_diario(models.Model):
    _name = 'balance.diario'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for e in self.browse(cr,uid, ids, context=context):
            name = "Balance dia " + e.fecha
            res.append((e['id'],name))
        return res

    def realizar_balance_diario(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            trabajo_obj = self.pool.get('trabajo.trabajo')
            line_obj = self.pool.get('balance.diario.line')

            #Datos de la tasa cambiaria
            tasa_obj = self.pool.get('tasa.cambiaria')
            tasa_ids = tasa_obj.search(cr, uid, [])
            tasa_id = tasa_obj.browse(cr, uid, tasa_ids[0])
            

            #eliminar las lineas previas en los resultados
            for line in record.balance_lines:
                line_obj.unlink(cr, uid, line.id, context=context)

            #Primero revisar el total de trabajos facturados en el dia
            fids = trabajo_obj.search(cr, uid, [('fecha', '=', record.fecha)])
            
            total_trabajos = len(fids)

            name = "Total de trabajos"
            descripcion = str(total_trabajos)
            nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #Total facturado y equivalente en CUC
            total_mn = total_cuc = propinas = 0
            for t in fids:
                trabajo_id = trabajo_obj.browse(cr, uid, t, context=context)
                total_mn += trabajo_id.importe_mn 
                total_cuc += trabajo_id.importe_cuc
                propinas += trabajo_id.total_propina

            name = "Importe total MN"
            descripcion = str(total_mn)
            nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            name = "Equivalente en CUC"
            descripcion = str(total_cuc)
            nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #Comprobar si cuadra la caja
            total_cierre = (record.total_mn + record.total_cuc * tasa_id.cup) #multiplico la cantidad de CUC por la tasa cambiaria actual
            #se resta el fondo de caja
            total_cierre -= record.fondo_caja
            #ahora se resta el esperado, que es el total en MN
            total_cierre -= total_mn + propinas
            #tiene que ser igual que 0 para que cuadre la caja
            #si es negativo falta dinero en la caja
            #si es positivo sobra dinero (faltan trabajos por declarar)
            name = "¿Correspondencia Caja - Ingresos?"
            descripcion = ""
            flag = False
            if total_cierre == 0:
                descripcion = "OK"
            elif total_cierre < 0:
                descripcion = "Faltan $%d" %(0-total_cierre) #para que salga +
                flag = True
            else:
                descripcion = "Sobran $%d" %(total_cierre)
                flag = True


            nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            if not flag:

                #cambiar el estado de los trabajos si no hay error
                for t in fids:
                    trabajo_obj.write(cr, uid, t, {'state': 'done'})

                #reponer en caja
                name = "Reponer en caja (Fondo de caja)"
                descripcion = str(record.fondo_caja)
                nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)

                #propinas
                name = "Propinas"
                descripcion = str(propinas)
                nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)

                #el resto para guardar
                name = "Importe de %s" %(record.dia_str)
                total_cierre = (record.total_mn - propinas + record.total_cuc * tasa_id.cup) #multiplico la cantidad de CUC por la tasa cambiaria actual
                total_cierre -= record.fondo_caja
                descripcion = str(total_cierre)
                nids = line_obj.preparar_linea_balance_diario(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)

                

                #actualizar el importe mn y equivalente cuc
                equivalente_cuc = total_cierre/tasa_id.cup
                record.update({'importe_mn': total_cierre, 'importe_cuc': equivalente_cuc, 'error': flag})


        return True

    def confirmar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if not record.balance_lines:
                raise osv.except_osv(_('Error!'),_("No puede archivar un balance sin antes realizar el análisis."))
            if record.error:
                raise osv.except_osv(_('Error!'),_("No puede archivar un balance con errores."))


            record.update({'state': 'done'})
            
            #repartir entre los empleados el total del cierre diario
            empleado_obj = self.pool.get('empleado.empleado')
            empleado_ids = empleado_obj.search(cr, uid, [], context=context)
            cobro_pendiente_obj = self.pool.get('cobros.pendientes.line')
               
            if empleado_ids:
                for empleado in empleado_ids:
                    empleado_id = empleado_obj.browse(cr, uid, empleado, context=context)
                    cobrar = record.importe_mn * empleado_id.salario / 100
                    name = "Balance diario"
                    vals = cobro_pendiente_obj.preparar_cobro(self, cr, empleado, cobrar, name)
                    cobro_pendiente_obj.create(cr, uid, vals, context=context)
        return True

    @api.depends('fecha')
    def _get_dia_str(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            DATETIME_FORMAT = "%Y-%m-%d"
            aux = datetime.strptime(record.fecha,DATETIME_FORMAT)
            dia = dias[aux.weekday()]
            record.update({'dia_str': dia})

    fecha = fields.Date('Fecha')
    dia_str = fields.Char('Dia semana', compute='_get_dia_str')
    fondo_caja = fields.Float('Fondo de caja (MN)', help="Indica el fondo en caja para movimientos financieros del dia. Es un dinero extra existente para cambios u otras eventualidades.")
    
    total_mn = fields.Float('Total MN', help="Indica el total de MN en caja al cierre del dia.")
    total_cuc = fields.Float('Total CUC', help="Indica el total de CUC en caja al cierre del dia.")

    importe_mn = fields.Float('Importe MN')
    importe_cuc = fields.Float('Equivalente CUC')

    error = fields.Boolean('Error')



    balance_lines = fields.One2many('balance.diario.line', 'balance_diario_id', 'Balance Diario Line')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Archivado'),
        ], 'Estado', default='draft', help="Un balance diario pasa a Archivado cuando se realiza el balance semanal que lo contiene.")

    _defaults={
        'fecha': fields.Date.today,
        'fondo_caja': 0,
    }

    _order="fecha desc"

class balance_diario_line(models.Model):
    _name="balance.diario.line"

    def preparar_linea_balance_diario(self, cr, uid, ids, balance_id, name, descripcion, context=None):
        vals = {
            'balance_diario_id': balance_id,
            'name': name,
            'descripcion': descripcion,
        }
        return vals

    balance_diario_id = fields.Many2one('balance.diario', 'Balance',  select=True, ondelete='cascade')
    name = fields.Char('Descripcion')
    descripcion = fields.Char('Detalles')
