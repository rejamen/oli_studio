# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Solucións Aloxa S.L. <info@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name': "oli_hhrr",

    'summary': """
        Control de Empleados.""",

    'description': """
        Facilita el control de empleados.
    """,

    'author': "OliStudio",
    'website': "http://www.olistudio.com",

    'version': '0.1',

    'depends': ['base'],

    # always loaded
    'data': [
        'views/hhrr.xml',
        'empleado.xml',
        'empleado_data.xml',
        'nomina.xml',
    ],
    # only loaded in demonstration mode
    'demo': [        
    ],
    "installable": True,
}
