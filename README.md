# Documentación del Sistema AgroMax

## Autores
- Kevin Possos  
- Wilman Porto  

## Introducción
Este documento describe el funcionamiento, componentes y estructura general del sistema de ventas **AgroMax**, una aplicación de escritorio desarrollada en Python utilizando Tkinter como interfaz gráfica y Firebase Realtime Database como backend. El objetivo principal es ofrecer una herramienta completa para la gestión de inventarios, ventas, facturación, fiados y reportes.

## Descripción General del Sistema
AgroMax está diseñado para pequeños comercios agrícolas que requieren herramientas simples y eficientes para manejar productos, registrar ventas, generar facturas en PDF, administrar fiados y generar reportes.

Incluye:
- Administración de productos  
- Caja (ventas)  
- Inventario visual  
- Facturación PDF  
- Módulo de fiados  
- Reportes semanales y mensuales  
- Integración con FTP para imágenes  
- Firebase para almacenar datos en tiempo real  

## Arquitectura del Sistema
El sistema está construido sobre una arquitectura modular:
- **Tkinter** para interfaz gráfica  
- **Firebase** para base de datos  
- **FTP** para imágenes  
- **ReportLab** para facturas PDF  
- **OpenPyXL** para reportes Excel  

## Módulos Principales

### 1. Módulo de Inicio
Pantalla principal que muestra el logo y las secciones del sistema.

### 2. Módulo de Administración
Permite:
- Registrar productos  
- Editarlos  
- Eliminarlos  
- Subir imágenes a FTP  
- Ver inventario completo en una tabla  

### 3. Módulo de Inventario
Muestra los productos con imagen, nombre, precio y un botón de descripción.

### 4. Módulo de Caja
Permite:
- Buscar productos por código o nombre  
- Agregar productos al carrito  
- Calcular totales  
- Generar factura  
- Guardar ventas en Firebase  
- Descontar stock automáticamente  

### 5. Módulo de Facturas
Muestra todas las facturas guardadas en Firebase y permite abrir el PDF asociado.

### 6. Módulo de Fiados
Funcionalidades:
- Registrar fiados  
- Editarlos desde una tabla  
- Eliminar registros  
- Asignar una factura a cada fiado y abrirla  

### 7. Módulo de Reportes
Genera:
- Reporte semanal en Excel  
- Reporte mensual en Excel  
- Producto más vendido  

## Consideraciones Técnicas
- Tkinter para GUI  
- Firebase Realtime Database como backend  
- ReportLab para facturas  
- OpenPyXL para reportes  
- FTP para imágenes  

## Presentación y Demostración del Sistema AGROMAX

Para una explicación visual y detallada del funcionamiento de la aplicación, el flujo de ventas y la interfaz de usuario, puede ver el video de presentación oficial del proyecto:

[![Video de Presentación AGROMAX](https://img.youtube.com/vi/aqIFYVvje08/0.jpg)](https://youtu.be/aqIFYVvje08)

**Enlace Directo:** [Ver Presentación del Proyecto en YouTube](https://youtu.be/aqIFYVvje08)


## Conclusión
AgroMax es una herramienta completa para apoyar la gestión de inventarios y ventas en negocios agrícolas. Su arquitectura modular permite mantener y escalar el sistema fácilmente.
