# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _

from datetime import datetime,date
from datetime import timedelta
import time
from time import strftime
from dateutil.relativedelta import relativedelta





class balance_semanal(models.Model):
    _name = 'balance.semanal'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = "Balance semana " + e.fecha_inicio + " - " + e.fecha_fin
	  		res.append((e['id'],name))
	  	return res

    def realizar_balance_semanal(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            trabajo_obj = self.pool.get('trabajo.trabajo')
            line_obj = self.pool.get('balance.semanal.line')
            balance_diario_obj = self.pool.get('balance.diario')
            cuenta_pagar_obj = self.pool.get('cuenta.pagar')

            #Datos de la tasa cambiaria
            tasa_obj = self.pool.get('tasa.cambiaria')
            tasa_ids = tasa_obj.search(cr, uid, [])
            tasa_id = tasa_obj.browse(cr, uid, tasa_ids[0])
            

            #eliminar las lineas previas en los resultados
            for line in record.balance_lines:
                line_obj.unlink(cr, uid, line.id, context=context)

            #Primero revisar el total de trabajos facturados en la semana
            fids = trabajo_obj.search(cr, uid, [('fecha', '>=', record.fecha_inicio),('fecha', '<=', record.fecha_fin)])
            total_trabajos = len(fids)

            name = "Total de trabajos"
            descripcion = str(total_trabajos)
            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #Total facturado y equivalente en CUC
            total_mn = total_cuc = 0
            for t in fids:
                trabajo_id = trabajo_obj.browse(cr, uid, t, context=context)
                total_mn += trabajo_id.importe_mn 
                total_cuc += trabajo_id.importe_cuc

            name = "Importe total MN"
            descripcion = str(total_mn)
            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            name = "Equivalente en CUC"
            descripcion = str(total_cuc)
            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #Comprobar si se corresponde el balanace semanal con los diarios
            #tomar los balances diarios de la semana
            diario_mn = diario_cuc = 0
            bids = balance_diario_obj.search(cr, uid, [('fecha', '>=', record.fecha_inicio),('fecha', '<=', record.fecha_fin)])
            for b in bids:
                balance_id = balance_diario_obj.browse(cr, uid, b, context=context)
                diario_mn += balance_id.importe_mn 
                diario_cuc += balance_id.importe_cuc

            calculado = diario_mn 

            #diario_mn y total_mn tienen que ser iguales, asi como 
            #diario_cuc y total_cuc para que exista correspondencia

            name = "¿Correspondencia Diarios - Semanal?"
            flag = False
            descripcion = ""
            if diario_mn == total_mn: #por consiguiente diario_cuc == total_cuc
                descripcion = "OK"
            else:
                descripcion = "ERROR"
                flag = True #bandera para no ejecutar la proxima linea del balance
            
            record.update({'error': flag})


            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #Para el total disponible, hay que buscar el empleado que corresponde
            #al taller, y ver que porciento de ganancia le corresponde, para
            #disponer del % indicado en sus datos solamente para pagar las cuentas
            nombre = "Oli Studio"
            empleado_obj = self.pool.get('empleado.empleado')
            fid = empleado_obj.search(cr, uid, [('name','=',nombre)])
                
            if not fid:
                raise osv.except_osv(_('Error!'),_("No se encuentra ningun empleado registrado como " + nombre))

            empleado_id = empleado_obj.browse(cr, uid, fid, context=context)

            #comprobar correspondencia entre ingresos semanal y
            #total especificado en el cierre de la semana manualmente
            total_cierre_semana = record.total_mn + record.total_cuc * tasa_id.cup
            total_disponible = total_cierre_semana * empleado_id.salario / 100

            name = "¿Correspondencia Balance Semanal - Ingresos de la semana?"
            descripcion = ""
            if flag:
                descripcion = "ERROR"
            else:
                if total_cierre_semana == calculado:
                    descripcion = "OK"
                else:
                    aux = total_cierre_semana - calculado
                    if aux > 0:
                        descripcion = "Sobran $%d" %(aux)
                        flag = True
                    else:
                        descripcion = "Faltan $%d" %(0 - aux)
                        flag = True
            record.update({'error': flag})

            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
            line_obj.create(cr, uid, nids, context=context)

            #actualizar estado de cuentas por pagar si no hay errores
            if flag:
                name = "_ESTADO DE CUENTAS_"
                descripcion = "ERROR"
                nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)
            else:
                name = "Disponible de la semana"
                descripcion = str(total_disponible)
                nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)
                
                name = "_ESTADO DE CUENTAS_"
                descripcion = ""
                nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                line_obj.create(cr, uid, nids, context=context)

                #tomo todas las cuentas
                #quedan ordenadas desde las mas prioritarias hasta las menos
                #comenzando de abajo hacia arriba

                
                fids = cuenta_pagar_obj.search(cr, uid, [('debe','!=',0)])
                if not fids: #todas pagadas
                    name = "Todas las cuentas están pagadas"
                    descripcion = ""
                    nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                    line_obj.create(cr, uid, nids, context=context)
                else:
                    for c in fids:
                        cuenta_id = cuenta_pagar_obj.browse(cr, uid, c)
                        
                        #para hacer el analisis se toma el valor total disponible y se va 
                        #distribuyendo en un arreglo de debitos y se le va restando el valor 
                        #en la posicion actual de ese arreglo mientras el total sea mayor que 0

                        aux = total_disponible - cuenta_id.debe
                        pagado = cuenta_id.pagado

                        if aux > 0: #alcanza para pagar completa la cuenta actual
                            pagado += cuenta_id.debe
                            total_disponible = aux 
                            cuenta_pagar_obj.write(cr, uid, c, {'pagado': pagado})
                            
                            if cuenta_id.prioridad > 0: 
                                cuenta_id.cuenta_pagada()

                            name = cuenta_id.name
                            descripcion = "Pagado %d - Debe %d" %(pagado,cuenta_id.debe)
                            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                            line_obj.create(cr, uid, nids, context=context)
                        else: #no alcanza, solo se paga parcialmente o lo paga completamente si es 0
                            pagado += total_disponible
                            total_disponible = 0
                            cuenta_pagar_obj.write(cr, uid, c, {'pagado': pagado})
                            name = cuenta_id.name
                            descripcion = "Pagado %d - Debe %d" %(pagado,cuenta_id.debe)
                            nids = line_obj.preparar_linea_balance_semanal(self, cr, uid, record.id, name, descripcion)
                            line_obj.create(cr, uid, nids, context=context)

                            if aux == 0:
                                if cuenta_id.prioridad > 0: 
                                    cuenta_id.cuenta_pagada()
                            
                            break;
                    

            #actualizar el importe mn y equivalente cuc
            mn = cuc = 0
            if not flag:
                cuc = total_cierre_semana/tasa_id.cup
                mn = total_cierre_semana
            record.update({'importe_mn': mn, 'importe_cuc': cuc})



        return True

    def confirmar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if not record.balance_lines:
                raise osv.except_osv(_('Error!'),_("No puede archivar un balance sin antes realizar el análisis."))
            if record.error:
                raise osv.except_osv(_('Error!'),_("No puede archivar un balance con errores."))


            record.update({'state': 'done'})
        return True

    def onchange_fecha_fin(self, cr, uid, ids, fecha_fin, context=None):
        result = {}
        if fecha_fin:
            DATETIME_FORMAT = "%Y-%m-%d"
            aux = datetime.strptime(fecha_fin,DATETIME_FORMAT)
            first_date = aux - relativedelta(days=5) #Getting 1st of next month
            result['fecha_inicio'] = first_date
        return {'value': result}

    def onchange_fecha_inicio(self, cr, uid, ids, fecha_fin, context=None):
        result = {}
        if fecha_fin:
            DATETIME_FORMAT = "%Y-%m-%d"
            aux = datetime.strptime(fecha_fin,DATETIME_FORMAT)
            last_date = aux + relativedelta(days=5) #Getting 1st of next month
            result['fecha_fin'] = last_date
        return {'value': result}

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')

    # dia_str = fields.Char('Dia semana', compute='_get_dia_str')
    # fondo_caja = fields.Float('Fondo de caja (MN)', help="Indica el fondo en caja para movimientos financieros del dia. Es un dinero extra existente para cambios u otras eventualidades.")
    
    total_mn = fields.Float('Total MN', help="Indica el total de MN en caja al cierre de la semana.")
    total_cuc = fields.Float('Total CUC', help="Indica el total de CUC en caja al cierre de la semana.")

    importe_mn = fields.Float('Importe MN')
    importe_cuc = fields.Float('Equivalente CUC')

    error = fields.Boolean('Error')


    balance_lines = fields.One2many('balance.semanal.line', 'balance_semanal_id', 'Balance Semanal Line')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Archivado'),
        ], 'Estado', default='draft')

    _defaults={
        'fecha_fin': fields.Date.today,
    }

    _order="fecha_inicio desc"

class balance_semanal_line(models.Model):
    _name="balance.semanal.line"

    def preparar_linea_balance_semanal(self, cr, uid, ids, balance_id, name, descripcion, context=None):
        vals = {
            'balance_semanal_id': balance_id,
            'name': name,
            'descripcion': descripcion,
        }
        return vals

    balance_semanal_id = fields.Many2one('balance.semanal', 'Balance',  select=True, ondelete='cascade')
    name = fields.Char('Descripcion')
    descripcion = fields.Char('Detalles')
