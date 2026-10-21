-- ===================================================================================
-- PRÁCTICA 2: ANÁLISIS INTEGRAL DE DATOS Y DETERMINACIÓN DE GANANCIAS POR REGIÓN
-- Base de Datos: northwind (MySQL 8.0)
-- Archivo: encargo1.sql
-- ===================================================================================
-- OBJETIVO:
-- Crear una consulta que muestre las ganancias por región de la base de datos de NorthWind,  --
-- deberán mostrar cada consulta que se utilizo para llegar a la consulta final, -- 
-- justificando cada paso siguieron para llegar a la consulta final. --
-- ===================================================================================

USE northwind;

-- ===================================================================================
-- FASE 1: RECONOCIMIENTO Y EXPLORACIÓN INICIAL DE TABLAS (Data Discovery)
-- Un ingeniero en bases de datos nunca escribe una consulta de agregación a ciegas.
-- Primero debe explorar la estructura del modelo relacional, las llaves foráneas,
-- las cardinalidades y la semántica de los atributos.
-- ===================================================================================

-- 1.1 Conteo general y exploración del catálogo de regiones (region)
-- Propósito: Identificar las regiones registradas formalmente en la empresa.
-- Hallazgo: Existen exactamente 4 regiones (1: Eastern, 2: Westerns, 3: Northern, 4: Southern).
-- NOTA TÉCNICA FORENSE: La columna 'RegionDescription' tiene tipo VARCHAR(50) y almacena
-- espacios en blanco de relleno (trailing spaces) procedentes de la migración original (NCHAR).
-- Por ello, todo tratamiento profesional debe aplicar TRIM() sobre esta columna.
SELECT COUNT(*) AS total_regiones FROM region;

SELECT 
    RegionID, 
    CONCAT('"', RegionDescription, '"') AS descripcion_con_espacios,
    LENGTH(RegionDescription) AS longitud_en_bytes,
    TRIM(RegionDescription) AS descripcion_limpia
FROM region;


-- 1.2 Exploración del catálogo geográfico de territorios (territories)
-- Propósito: Conocer los territorios comerciales y su asociación con las regiones (FK RegionID).
-- Hallazgo: Existen 53 territorios distribuidos entre las 4 regiones.
-- Distribución: Región 1 (19), Región 2 (15), Región 3 (11), Región 4 (8).
SELECT COUNT(*) AS total_territorios FROM territories;

SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    COUNT(t.TerritoryID) AS total_territorios_asignados
FROM region r
LEFT JOIN territories t ON r.RegionID = t.RegionID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY r.RegionID;

SELECT 
    TerritoryID, 
    TRIM(TerritoryDescription) AS territorio, 
    RegionID 
FROM territories 
LIMIT 10;


-- 1.3 Exploración de la asignación comercial empleado-territorio (employeeterritories)
-- Propósito: Inspeccionar la tabla puente que conecta a los vendedores con sus áreas de venta.
-- Hallazgo: Contiene 49 asignaciones activas.
-- OBSERVACIÓN CRÍTICA: La relación entre Empleados y Territorios es N:M (muchos a muchos).
-- Un solo empleado puede gestionar múltiples territorios. Esto representa un punto crítico de
-- riesgo de multiplicación cartesiana si se une directamente en consultas de facturación.
SELECT COUNT(*) AS total_asignaciones_empleado_territorio FROM employeeterritories;

SELECT 
    EmployeeID, 
    COUNT(TerritoryID) AS cantidad_territorios_asignados
FROM employeeterritories
GROUP BY EmployeeID
ORDER BY cantidad_territorios_asignados DESC;


-- 1.4 Exploración de la plantilla de vendedores (employees)
-- Propósito: Determinar el número total de empleados registrados en la compañía.
-- Hallazgo: Existen exactamente 9 empleados, todos ellos con rol operativo o directivo de ventas.
SELECT COUNT(*) AS total_empleados FROM employees;

SELECT 
    EmployeeID, 
    CONCAT(FirstName, ' ', LastName) AS nombre_completo, 
    Title AS cargo, 
    City AS ciudad_residencia, 
    Country AS pais 
FROM employees;


-- 1.5 Exploración de órdenes de compra (orders) y diagnóstico de campos regionales
-- Propósito: Inspeccionar cómo se relacionan los pedidos con los empleados y evaluar si existe
-- un campo de región directo en los pedidos (ShipRegion).
-- Hallazgo fundamental:
-- 1. Existen 830 órdenes en total; el 100% de ellas posee un EmployeeID válido asignado.
-- 2. La columna 'ShipRegion' de la tabla 'orders' tiene 507 valores NULL (61.08% de nulos)
--    y sus valores no corresponden a las regiones de la empresa (Eastern, Westerns, etc.),
--    sino a abreviaturas de estados o provincias de entrega (p. ej., 'WA', 'RJ', 'SP').
-- Conclusión de diseño: La verdadera región de negocio NO se obtiene de 'ShipRegion',
-- sino de la estructura organizacional: orders -> employees -> territories -> region.
SELECT COUNT(*) AS total_pedidos FROM orders;

SELECT 
    COUNT(*) AS total_pedidos,
    COUNT(EmployeeID) AS pedidos_con_vendedor,
    COUNT(ShipRegion) AS pedidos_con_shipregion,
    COUNT(*) - COUNT(ShipRegion) AS pedidos_con_shipregion_nulo,
    ROUND(((COUNT(*) - COUNT(ShipRegion)) / COUNT(*)) * 100, 2) AS porcentaje_nulos_shipregion
FROM orders;


-- 1.6 Exploración del detalle de órdenes (order details)
-- Propósito: Identificar las columnas financieras esenciales: UnitPrice (precio unitario),
-- Quantity (cantidad de artículos) y Discount (descuento aplicable).
-- Hallazgo: 2,155 líneas transaccionales de venta. En este dataset, Discount está en 0 para todas las líneas.
-- No obstante, la fórmula estándar de la industria debe contemplar siempre (1 - Discount).
SELECT COUNT(*) AS total_lineas_detalle FROM `order details`;

SELECT 
    OrderID, 
    ProductID, 
    UnitPrice, 
    Quantity, 
    Discount, 
    ROUND(UnitPrice * Quantity * (1 - Discount), 2) AS importe_linea
FROM `order details`
LIMIT 10;


-- ===================================================================================
-- FASE 2: ESTABLECER LA LÍNEA BASE DE VENTAS (Ground Truth Contable)
-- Un principio inviolable de la ingeniería de datos es definir la "cifra dorada" o
-- línea base oficial de la base de datos antes de construir cualquier reporte.
-- Ninguna consulta por región puede ser correcta si su suma no coincide al centavo
-- con el total registrado en la tabla transaccional de ventas.
-- ===================================================================================

-- 2.1 Cálculo del Total Global Facturado por Venta de Productos (Línea Base Oficial)
-- Propósito: Calcular el monto exacto facturado por la venta de productos: SUM(UnitPrice * Quantity * (1 - Discount)).
-- Cifra Oficial de Control: $1,354,458.59 en 51,317 unidades vendidas a lo largo de 830 pedidos.
-- Nota: Esta es la cifra contra la cual cualquier agrupación regional DEBE cuadrar obligatoriamente.
SELECT 
    COUNT(DISTINCT OrderID) AS total_pedidos_con_venta,
    SUM(Quantity) AS total_unidades_globales,
    ROUND(SUM(UnitPrice * Quantity * (1 - Discount)), 2) AS total_ventas_reales_empresa
FROM `order details`;


-- 2.2 Auditoría de Fletes de Envío (orders.Freight)
-- Propósito: Analizar el componente de fletes cobrados en los encabezados de las órdenes.
-- Resultado: $64,942.69 cobrados en fletes.
-- Si se analiza la Facturación Bruta Total (Productos + Fletes), el gran total es $1,419,401.28.
SELECT 
    COUNT(OrderID) AS total_ordenes,
    ROUND(SUM(Freight), 2) AS total_fletes_empresa,
    ROUND(
        (SELECT SUM(UnitPrice * Quantity * (1 - Discount)) FROM `order details`) + SUM(Freight), 
        2
    ) AS facturacion_total_integrada
FROM orders;


-- ===================================================================================
-- FASE 3: EL INTENTO INGENUO Y LA GRAN DISCREPANCIA (El Error Común)
-- El error más frecuente cometido por desarrolladores inexpertos consiste en enlazar
-- todas las tablas en serie mediante INNER JOIN directamente:
-- `order details` -> orders -> employees -> employeeterritories -> territories -> region.
-- A continuación reproducimos y auditamos este enfoque.
-- ===================================================================================

-- 3.1 Primer intento ingenuo uniendo todas las tablas en cadena directa
-- Propósito: Unir las tablas y sumar las ventas agrupando por región.
-- Resultado: Aparentemente devuelve las 4 regiones con sumas millonarias.
SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_calculada_ingenua
FROM `order details` od
INNER JOIN orders o ON od.OrderID = o.OrderID
INNER JOIN employees e ON o.EmployeeID = e.EmployeeID
INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
INNER JOIN region r ON t.RegionID = r.RegionID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY r.RegionID;


-- 3.2 Comprobación matemática: Sumar los resultados del intento ingenuo
-- Propósito: Auditar si la suma de las regiones coincide con la Línea Base Contable ($1,354,458.59).
-- ¡ALERTA CRÍTICA DE DISCREPANCIA!:
-- Suma obtenida con el JOIN ingenuo:  $6,698,176.56
-- Ventas reales de la empresa:        $1,354,458.59
-- ¡HAY UN DESFASE ASTRONÓMICO DE +$5,343,717.97 (+394.5% DE ERROR)!
-- Las cifras están multiplicadas y viciadas por completo.
SELECT 
    ROUND(SUM(ganancia_calculada_ingenua), 2) AS suma_total_ingenuo,
    (SELECT ROUND(SUM(UnitPrice * Quantity * (1 - Discount)), 2) FROM `order details`) AS venta_real_empresa,
    ROUND(SUM(ganancia_calculada_ingenua) - (SELECT SUM(UnitPrice * Quantity * (1 - Discount)) FROM `order details`), 2) AS desfase_inflado
FROM (
    SELECT 
        SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS ganancia_calculada_ingenua
    FROM `order details` od
    INNER JOIN orders o ON od.OrderID = o.OrderID
    INNER JOIN employees e ON o.EmployeeID = e.EmployeeID
    INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    INNER JOIN region r ON t.RegionID = r.RegionID
    GROUP BY r.RegionID
) AS subconsulta;


-- ===================================================================================
-- FASE 4: AUDITORÍA FORENSE DE LA BASE DE DATOS (Diagnóstico de Causa Raíz)
-- En esta fase investigamos las causas exactas por las cuales $6,698,176.56 != $1,354,458.59.
-- Analizamos la relación entre empleados, territorios y regiones para entender el origen
-- matemático exacto de la multiplicación cartesiana.
-- ===================================================================================

-- 4.1 INVESTIGACIÓN 1: Multiplicidad en la tabla 'employeeterritories'
-- Propósito: Determinar cuántos territorios tiene asignado cada empleado en 'employeeterritories'.
-- Hallazgos:
--   - Empleado 7 (Robert King):       10 territorios asignados.
--   - Empleado 2 (Andrew Fuller):      7 territorios asignados.
--   - Empleado 5 (Steven Buchanan):    7 territorios asignados.
--   - Empleado 9 (Anne Dodsworth):     7 territorios asignados.
--   - Empleado 6 (Michael Suyama):     5 territorios asignados.
--   - Empleado 3 (Janet Leverling):    4 territorios asignados.
--   - Empleado 8 (Laura Callahan):     4 territorios asignados.
--   - Empleado 4 (Margaret Peacock):   3 territorios asignados.
--   - Empleado 1 (Nancy Davolio):      2 territorios asignados.
-- EFECTO EN EL JOIN INGENUO:
-- Al enlazar 'orders' con 'employeeterritories', cada pedido de Robert King se multiplica por 10,
-- cada pedido de Andrew Fuller se multiplica por 7, y así sucesivamente con cada vendedor.
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS empleado,
    COUNT(et.TerritoryID) AS total_territorios_del_empleado
FROM employees e
INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
GROUP BY e.EmployeeID, e.FirstName, e.LastName
ORDER BY total_territorios_del_empleado DESC;


-- 4.2 INVESTIGACIÓN 2: Verificación de Unicidad Regional por Empleado
-- Pregunta clave del analista: ¿Un empleado atiende territorios en más de una región?
-- Propósito: Comprobar si algún vendedor opera en múltiples regiones geográficas.
-- Hallazgo crucial:
-- El campo 'COUNT(DISTINCT t.RegionID)' es exactamente 1 para TODOS los empleados:
--   - Empleados 1, 2, 4, 5 pertenecen exclusivamente a la Región 1 (Eastern).
--   - Empleados 6, 7 pertenecen exclusivamente a la Región 2 (Westerns).
--   - Empleados 8, 9 pertenecen exclusivamente a la Región 3 (Northern).
--   - Empleado 3 pertenece exclusivamente a la Región 4 (Southern).
-- CONCLUSIÓN ARQUITECTÓNICA:
-- La pertenencia de un empleado a una región es 1 a 1 (unívoca). No hay cruce interregional.
-- La multiplicación ocurre exclusivamente porque el empleado atiende varios territorios DENTRO
-- de su misma región. Por tanto, no se debe hacer JOIN directo con 'employeeterritories',
-- sino obtener la relación única Empleado -> Región (proyección desacoplada con DISTINCT).
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS empleado,
    COUNT(DISTINCT t.RegionID) AS regiones_distintas_del_empleado,
    MIN(t.RegionID) AS id_region_unica,
    TRIM(MIN(r.RegionDescription)) AS nombre_region_unica,
    COUNT(et.TerritoryID) AS territorios_en_esa_region
FROM employees e
INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
INNER JOIN region r ON t.RegionID = r.RegionID
GROUP BY e.EmployeeID, e.FirstName, e.LastName
ORDER BY e.EmployeeID;


-- 4.3 CONCILIACIÓN MATEMÁTICA FORENSE DE LA DISCREPANCIA INGENUA
-- Demostración de cómo la multiplicación por territorio reconstruye con exactitud
-- cada centavo del error ingenuo por región:
--
-- Región 1 (Eastern):
--   - Nancy Davolio (2 terr):      $202,143.71 * 2 =   $404,287.42
--   - Andrew Fuller (7 terr):      $177,749.26 * 7 = $1,244,244.82
--   - Margaret Peacock (3 terr):   $250,187.45 * 3 =   $750,562.35
--   - Steven Buchanan (7 terr):     $75,567.75 * 7 =   $528,974.25
--   Subtotal ingenuo Eastern:                        $2,928,068.84  (Venta Real: $705,648.17)
--
-- Región 2 (Westerns):
--   - Michael Suyama (5 terr):      $78,198.10 * 5 =   $390,990.50
--   - Robert King (10 terr):       $141,295.99 * 10 = $1,412,959.90
--   Subtotal ingenuo Westerns:                       $1,803,950.40  (Venta Real: $219,494.09)
--
-- Región 3 (Northern):
--   - Laura Callahan (4 terr):     $133,301.03 * 4 =   $533,204.12
--   - Anne Dodsworth (7 terr):      $82,964.00 * 7 =   $580,748.00
--   Subtotal ingenuo Northern:                       $1,113,952.12  (Venta Real: $216,265.03)
--
-- Región 4 (Southern):
--   - Janet Leverling (4 terr):    $213,051.30 * 4 =   $852,205.20  (Venta Real: $213,051.30)
--
-- Suma de las 4 regiones ingenuas:                   $6,698,176.56  (Venta Real: $1,354,458.59)
-- ¡La causa raíz de la inflación del 394.5% queda demostrada de forma concluyente!
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS empleado,
    TRIM(r.RegionDescription) AS region,
    terr.num_territorios AS factor_multiplicacion_territorios,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS venta_real_empleado,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) * terr.num_territorios, 2) AS venta_inflada_en_join_ingenuo
FROM employees e
INNER JOIN (
    SELECT EmployeeID, COUNT(TerritoryID) AS num_territorios
    FROM employeeterritories
    GROUP BY EmployeeID
) terr ON e.EmployeeID = terr.EmployeeID
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON e.EmployeeID = emp_reg.EmployeeID
INNER JOIN region r ON emp_reg.RegionID = r.RegionID
INNER JOIN orders o ON e.EmployeeID = o.EmployeeID
INNER JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY e.EmployeeID, e.FirstName, e.LastName, r.RegionDescription, terr.num_territorios
ORDER BY r.RegionDescription, venta_real_empleado DESC;


-- 4.4 INVESTIGACIÓN 4: La trampa de la duplicación de fletes (orders.Freight)
-- Al combinar encabezados de órdenes con detalles de órdenes, un error clásico es sumar o.Freight
-- dentro del mismo JOIN con `order details`.
-- Hallazgo: Como cada pedido tiene en promedio 2.6 líneas de detalle en `order details`,
-- sumar o.Freight directamente infla los fletes de $64,942.69 a $207,306.10 (+219% de inflación).
-- Regla de ingeniería: Las métricas de nivel 'orden' (como flete) deben agregarse de forma separada
-- o calcularse agrupando previamente a nivel OrderID.
SELECT 
    (SELECT ROUND(SUM(Freight), 2) FROM orders) AS flete_real_global,
    ROUND(SUM(o.Freight), 2) AS flete_duplicado_por_join_con_detalles,
    ROUND(SUM(o.Freight) - (SELECT SUM(Freight) FROM orders), 2) AS distorsion_por_duplicidad
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID;


-- ===================================================================================
-- FASE 5: CONSTRUCCIÓN ITERATIVA DE LA SOLUCIÓN
-- Con los hallazgos de la auditoría, construimos de manera controlada y robusta
-- la consulta correcta que garantiza la fidelidad de los datos.
-- ===================================================================================

-- 5.1 Desacoplamiento de la relación Empleado -> Región (Eliminación de la multiplicidad)
-- Propósito: Crear una tabla derivada limpia que proyecte un único registro por cada vendedor
-- con su correspondiente RegionID, sin arrastrar los 49 territorios.
SELECT DISTINCT 
    et.EmployeeID, 
    t.RegionID
FROM employeeterritories et
INNER JOIN territories t ON et.TerritoryID = t.TerritoryID;


-- 5.2 Consulta inicial corregida de ventas por región
-- Propósito: Probar el enlace desacoplado contra `order details`.
-- Comprobación:
--   - Eastern:  $705,648.17
--   - Westerns: $219,494.09
--   - Northern: $216,265.03
--   - Southern: $213,051.30
-- Suma total: $1,354,458.59. ¡Cuadra al centavo con la Línea Base Contable!
SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_total_productos
FROM region r
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
INNER JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
INNER JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY ganancia_total_productos DESC;


-- 5.3 Asegurar la inclusión de todas las regiones mediante LEFT JOIN y COALESCE
-- Propósito: Garantizar que si alguna región hipotéticamente tuviese $0.00 de ventas,
-- aparezca en el reporte con valor 0 en lugar de ser omitida del análisis gerencial.
SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    COUNT(DISTINCT o.OrderID) AS total_pedidos,
    COALESCE(SUM(od.Quantity), 0) AS total_unidades_vendidas,
    ROUND(COALESCE(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 0), 2) AS ganancia_total_productos
FROM region r
LEFT JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
LEFT JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
LEFT JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY ganancia_total_productos DESC;


-- ===================================================================================
-- FASE 6: DEFINICIÓN DE CRITERIOS DE NEGOCIO Y VARIANTES FINANCIERAS
-- En el análisis financiero corporativo existen dos lecturas válidas de "Ganancias por Región":
--
-- Criterio 1: Ventas Netas de Productos (Mercancía Vendida)
--   Fórmula: SUM(od.UnitPrice * od.Quantity * (1 - od.Discount))
--   Monto Total Empresa: $1,354,458.59
--
-- Criterio 2: Facturación Total Integrada (Productos Netos + Fletes por Región)
--   Fórmula: Venta de Productos + Flete facturado en las órdenes de los empleados de la región.
--   Monto Total Empresa: $1,419,401.28 ($1,354,458.59 + $64,942.69 de flete).
-- ===================================================================================

-- 6.1 Desglose de Ventas por Empleado dentro de cada Región (Auditoría Interna de Aporte)
-- Propósito: Mostrar con total transparencia qué vendedor generó los ingresos de cada región.
SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS empleado,
    COUNT(DISTINCT o.OrderID) AS pedidos_atendidos,
    COALESCE(SUM(od.Quantity), 0) AS unidades_vendidas,
    ROUND(COALESCE(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 0), 2) AS venta_neta_empleado
FROM region r
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
INNER JOIN employees e ON emp_reg.EmployeeID = e.EmployeeID
LEFT JOIN orders o ON e.EmployeeID = o.EmployeeID
LEFT JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY r.RegionID, r.RegionDescription, e.EmployeeID, e.FirstName, e.LastName
ORDER BY r.RegionID, venta_neta_empleado DESC;


-- 6.2 Consulta con Criterio 2: Integración de Fletes sin Duplicación
-- Propósito: Pre-agregar los detalles de órdenes para que el flete no se multiplique por el número de líneas.
SELECT 
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    COUNT(DISTINCT o.OrderID) AS total_pedidos,
    SUM(items.unidades_pedido) AS total_unidades,
    ROUND(SUM(items.venta_pedido), 2) AS venta_neta_productos,
    ROUND(SUM(o.Freight), 2) AS total_fletes_cobrados,
    ROUND(SUM(items.venta_pedido + o.Freight), 2) AS facturacion_total_integrada
FROM region r
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
INNER JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
INNER JOIN (
    SELECT 
        OrderID,
        SUM(Quantity) AS unidades_pedido,
        SUM(UnitPrice * Quantity * (1 - Discount)) AS venta_pedido
    FROM `order details`
    GROUP BY OrderID
) items ON o.OrderID = items.OrderID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY facturacion_total_integrada DESC;


-- ===================================================================================
-- FASE 7: CONSULTAS FINALES (Entregables Oficiales)
-- A continuación se presentan las dos consultas finales:
-- 7.1 La Consulta Estándar Directa: Limpia, directa y minimalista según el requerimiento.
-- 7.2 La Master Query Ejecutiva: Con todos los KPIs de dirección comercial y formato profesional.
-- ===================================================================================

-- 7.1 CONSULTA ESTÁNDAR DIRECTA (Respuesta Concisa del Encargo 1)
-- Propósito: Responder puntualmente a "mostrar las ganancias por región".
SELECT 
    r.RegionID AS id_region,
    TRIM(r.RegionDescription) AS region,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancias_totales
FROM region r
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
INNER JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
INNER JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY ganancias_totales DESC;


-- 7.2 CONSULTA FINAL DEFINITIVA EJECUTIVA (Master Query Profesional)
-- Esta es la consulta principal recomendada para entrega de alto nivel.
-- Cumple con todos los estándares profesionales:
-- 1. Resuelve la duplicación cartesiana de 'employeeterritories' desacoplando el mapeo Empleado -> Región.
-- 2. Elimina espacios en blanco residuales de 'RegionDescription' mediante TRIM().
-- 3. Previene la inflación de fletes mediante pre-agrupación a nivel OrderID.
-- 4. Incluye métricas clave: Fuerza de ventas (vendedores), pedidos, unidades, ventas, fletes,
--    facturación total, porcentaje de participación nacional y ticket promedio por pedido.
-- 5. Manejo seguro de nulos mediante LEFT JOIN y COALESCE.
-- 6. Nombres de columnas limpios y legibles para reportes ejecutivos.
SELECT 
    r.RegionID AS 'ID Región',
    TRIM(r.RegionDescription) AS 'Región',
    COUNT(DISTINCT e.EmployeeID) AS 'Fuerza de Ventas (Vendedores)',
    COUNT(DISTINCT o.OrderID) AS 'Total Pedidos',
    COALESCE(SUM(sub_ord.total_unidades), 0) AS 'Unidades Vendidas',
    ROUND(COALESCE(SUM(sub_ord.venta_productos), 0), 2) AS 'Ganancias Productos ($)',
    ROUND(COALESCE(SUM(o.Freight), 0), 2) AS 'Fletes Facturados ($)',
    ROUND(COALESCE(SUM(sub_ord.venta_productos + o.Freight), 0), 2) AS 'Facturación Total ($)',
    ROUND(
        (COALESCE(SUM(sub_ord.venta_productos), 0) / 
        (SELECT SUM(UnitPrice * Quantity * (1 - Discount)) FROM `order details`)) * 100, 
        2
    ) AS '% Participación Ventas',
    ROUND(
        COALESCE(SUM(sub_ord.venta_productos), 0) / NULLIF(COUNT(DISTINCT o.OrderID), 0), 
        2
    ) AS 'Ticket Promedio ($)'
FROM region r
LEFT JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON r.RegionID = emp_reg.RegionID
LEFT JOIN employees e ON emp_reg.EmployeeID = e.EmployeeID
LEFT JOIN orders o ON e.EmployeeID = o.EmployeeID
LEFT JOIN (
    SELECT 
        OrderID,
        SUM(Quantity) AS total_unidades,
        SUM(UnitPrice * Quantity * (1 - Discount)) AS venta_productos
    FROM `order details`
    GROUP BY OrderID
) sub_ord ON o.OrderID = sub_ord.OrderID
GROUP BY r.RegionID, r.RegionDescription
ORDER BY `Ganancias Productos ($)` DESC;


-- ===================================================================================
-- FASE 8: ANEXO DE AUDITORÍA Y CONCILIACIÓN CONTABLE DEFINITIVA
-- Propósito: Demostrar matemáticamente que la consulta final no perdió ni duplicó
-- un solo centavo de los $1,354,458.59 registrados en la base de datos de Northwind.
-- Reconciliación:
--   - Suma total de las 4 regiones:      $1,354,458.59
--   - Línea base de control de ventas:   $1,354,458.59
--   - Discrepancia / Descuadre:                 $0.00 (100.00% exacto)
-- ===================================================================================

SELECT 
    '1. Ganancias Sumadas por Región' AS Concepto,
    ROUND(SUM(sub.ganancia_region), 2) AS Monto_Total,
    'Suma agregada de las 4 regiones (Eastern, Westerns, Northern, Southern)' AS Auditoria
FROM (
    SELECT 
        r.RegionID,
        SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS ganancia_region
    FROM region r
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON r.RegionID = emp_reg.RegionID
    INNER JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    GROUP BY r.RegionID
) sub

UNION ALL

SELECT 
    '2. Total Global Facturado (Línea Base Oficial)' AS Concepto,
    ROUND(SUM(UnitPrice * Quantity * (1 - Discount)), 2) AS Monto_Total,
    'Control contable sin JOINs sobre la tabla `order details`' AS Auditoria
FROM `order details`

UNION ALL

SELECT 
    '3. Diferencia Contable (Discrepancia)' AS Concepto,
    ROUND(
        (SELECT SUM(sub.ganancia_region) FROM (
            SELECT SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS ganancia_region
            FROM region r
            INNER JOIN (
                SELECT DISTINCT et.EmployeeID, t.RegionID
                FROM employeeterritories et
                INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
            ) emp_reg ON r.RegionID = emp_reg.RegionID
            INNER JOIN orders o ON emp_reg.EmployeeID = o.EmployeeID
            INNER JOIN `order details` od ON o.OrderID = od.OrderID
            GROUP BY r.RegionID
        ) sub) 
        - 
        (SELECT SUM(UnitPrice * Quantity * (1 - Discount)) FROM `order details`), 
        2
    ) AS Monto_Total,
    'Diferencia = $0.00 -> Conciliación y Cuadre Matemático al 100%' AS Auditoria;
