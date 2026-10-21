-- ===================================================================================
-- PRÁCTICA 2: ANÁLISIS INTEGRAL DE DATOS Y DETERMINACIÓN DE PRODUCTOS MENOS VENDIDOS
-- Base de Datos: northwind (MySQL 8.0)
-- Archivo: encargo2.sql
-- ===================================================================================
-- OBJETIVO:
-- Crear una consulta que genere una tabla donde se muestren los productos que
-- menos se vendieron por región, donde el año y las 4 regiones sean las columnas,
-- y en cada celda se muestre el producto (o productos) con su ganancia asociada.
-- Se documenta todo el proceso lógico, exploración de datos, diagnóstico de trampas
-- del modelo relacional, criterios de desempate y validación celda por celda.
-- ===================================================================================

USE northwind;

-- ===================================================================================
-- FASE 1: RECONOCIMIENTO Y EXPLORACIÓN INICIAL DE TABLAS (Data Discovery)
-- Antes de construir una matriz pivoteada compleja, un analista de datos debe
-- entender el dominio temporal de la base, la cobertura del catálogo de productos
-- y la cardinalidad de las ventas por período y zona geográfica.
-- ===================================================================================

-- 1.1 Exploración del horizonte temporal de ventas (orders)
-- Propósito: Determinar los años disponibles en el historial de órdenes de Northwind.
-- Hallazgo: Existen 3 años de operación:
--   - 1996: 152 órdenes (operación en el segundo semestre: jul-dic).
--   - 1997: 408 órdenes (año completo: ene-dic).
--   - 1998: 270 órdenes (primer cuatrimestre: ene-may).
-- Total de órdenes en el sistema: 830.
SELECT 
    YEAR(OrderDate) AS anio_operacion,
    MIN(OrderDate) AS primer_pedido,
    MAX(OrderDate) AS ultimo_pedido,
    COUNT(OrderID) AS total_pedidos
FROM orders
GROUP BY YEAR(OrderDate)
ORDER BY anio_operacion;


-- 1.2 Exploración del catálogo de productos (products)
-- Propósito: Conocer la cantidad total de productos activos o descontinuados en la empresa.
-- Hallazgo: Existen 77 productos en el catálogo comercial, con precios que van desde
-- $2.50 (Geitost) hasta $263.50 (Côte de Blaye).
SELECT 
    COUNT(*) AS total_productos_catalogo,
    MIN(UnitPrice) AS precio_minimo,
    MAX(UnitPrice) AS precio_maximo,
    ROUND(AVG(UnitPrice), 2) AS precio_promedio
FROM products;

SELECT 
    ProductID, 
    ProductName, 
    UnitPrice, 
    UnitsInStock, 
    Discontinued 
FROM products 
LIMIT 10;


-- 1.3 Cobertura y dispersión de productos vendidos por año y región
-- Propósito: Determinar cuántos productos distintos registraron al menos una venta
-- en cada región para cada año.
-- Hallazgo: En ningún año/región se vendieron simultáneamente los 77 productos.
-- Por ejemplo, en 1996 en la región Southern solo se vendieron 37 productos distintos.
SELECT 
    YEAR(o.OrderDate) AS anio,
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    COUNT(DISTINCT od.ProductID) AS total_productos_con_venta
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
INNER JOIN region r ON emp_reg.RegionID = r.RegionID
GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription
ORDER BY anio, r.RegionID;


-- 1.4 Diagnóstico Metodológico: Productos con Ventas Activas vs. Productos con 0 Ventas
-- Pregunta de Negocio: ¿Qué significa "los productos que menos se vendieron"?
-- En minería de datos y analítica comercial, existen dos posibles interpretaciones:
--   Interpretación 1 (Catálogo Inactivo): Artículos del catálogo con 0 ventas registradas.
--     - En 1996 Southern, 40 productos tuvieron 0 ventas. Reportar una celda con 40 productos
--       con $0.00 de ganancia inutiliza la tabla para la toma de decisiones gerenciales.
--   Interpretación 2 (Mínimo de la Distribución Transaccional Activa): Artículos que registraron
--     movimiento de venta en el período, pero cuya demanda fue la más baja de la región.
--     - Además, el requerimiento solicita expresamente: "en la celda muestre los productos CON SU GANANCIA".
-- Conclusión de Ingeniería: El análisis debe evaluar la demanda mínima de productos vendidos (SUM > 0),
-- documentando además los dos criterios financieros: menor cantidad física (unidades) y menor recaudación (dólares).
SELECT 
    77 - COUNT(DISTINCT od.ProductID) AS productos_sin_ventas_1996_southern
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
WHERE YEAR(o.OrderDate) = 1996 AND emp_reg.RegionID = 4;


-- ===================================================================================
-- FASE 2: ESTABLECER LA LÍNEA BASE CONTABLE (Ground Truth por Período)
-- Para asegurar que los cálculos de ganancias de cada producto sean 100% exactos,
-- establecemos las cifras de control oficiales agrupadas por año.
-- ===================================================================================

-- 2.1 Cifras oficiales de facturación por año en 'order details'
-- Resultado de Control:
--   - 1996:   9,581 unidades vendidas | $226,298.50 facturados en 152 órdenes.
--   - 1997:  25,489 unidades vendidas | $658,388.75 facturados en 408 órdenes.
--   - 1998:  16,247 unidades vendidas | $469,771.34 facturados en 270 órdenes.
-- Gran Total Histórico: 51,317 unidades | $1,354,458.59 (Cuadre perfecto con Encargo 1).
SELECT 
    YEAR(o.OrderDate) AS anio,
    COUNT(DISTINCT o.OrderID) AS total_pedidos,
    SUM(od.Quantity) AS unidades_totales,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS facturacion_total_anual
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID
GROUP BY YEAR(o.OrderDate)
ORDER BY anio;


-- 2.2 Agregación base correcta por Año, Región y Producto
-- Propósito: Calcular el volumen en unidades y la ganancia monetaria neta por cada triada
-- (Año, Región, Producto), desacoplando el mapeo de empleados a territorios mediante DISTINCT
-- para evitar la multiplicación cartesiana ya descubierta en el Encargo 1.
SELECT 
    YEAR(o.OrderDate) AS anio,
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    p.ProductID,
    p.ProductName,
    SUM(od.Quantity) AS unidades_vendidas,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID
INNER JOIN products p ON od.ProductID = p.ProductID
INNER JOIN (
    SELECT DISTINCT et.EmployeeID, t.RegionID
    FROM employeeterritories et
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
INNER JOIN region r ON emp_reg.RegionID = r.RegionID
GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription, p.ProductID, p.ProductName
ORDER BY anio, r.RegionID, unidades_vendidas ASC
LIMIT 10;


-- ===================================================================================
-- FASE 3: EL INTENTO INGENUO Y LA CORRUPCIÓN DE LOS RANKINGS
-- En el Encargo 1 vimos que unir directamente 'employeeterritories' inflaba el dinero.
-- Pero en este Encargo 2 ocurre algo aún más grave:
-- ¡EL JOIN INGENUO MODIFICA EL ORDEN RELATIVO Y ARROJA PRODUCTOS COMPLETAMENTE EQUIVOCADOS!
-- ===================================================================================

-- 3.1 Consulta de ranking con JOIN ingenuo a 'employeeterritories'
-- Si un desarrollador realiza INNER JOIN directo con 'employeeterritories', las ventas
-- de los empleados con más territorios (e.g., Andrew con 7, Steven con 7) se multiplican
-- mucho más que las de empleados con menos territorios (e.g., Nancy con 2, Margaret con 3).
-- Esto distorsiona las proporciones y cambia cuál es el producto "menos vendido".
SELECT 
    YEAR(o.OrderDate) AS anio,
    r.RegionID,
    TRIM(r.RegionDescription) AS region,
    p.ProductID,
    p.ProductName,
    SUM(od.Quantity) AS unidades_ingenuas_infladas,
    ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_ingenua_inflada
FROM orders o
INNER JOIN `order details` od ON o.OrderID = od.OrderID
INNER JOIN products p ON od.ProductID = p.ProductID
INNER JOIN employees e ON o.EmployeeID = e.EmployeeID
INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
INNER JOIN region r ON t.RegionID = r.RegionID
GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription, p.ProductID, p.ProductName
LIMIT 5;


-- 3.2 DEMOSTRACIÓN FORENSE DEL ERROR INGENUO (Comparación de Productos Identificados)
-- Observemos cómo el JOIN ingenuo altera la verdad histórica:
--
-- 1. En 1996 - Eastern:
--    - PRODUCTO REAL MENOS VENDIDO: Laughing Lumberjack Lager (5 u., $56.00) y Genen Shouyu (5 u., $62.00).
--    - PRODUCTO ARROJADO POR EL JOIN INGENUO: Grandma's Boysenberry Spread (12 u. infladas).
--    ¿Por qué? Porque Lumberjack fue vendido por un empleado con 7 territorios (5 * 7 = 35 u. infladas),
--    mientras que Boysenberry Spread fue vendido por empleados con menos territorios, quedando artificialmente
--    con menor suma en el JOIN ingenuo.
--
-- 2. En 1996 - Westerns:
--    - PRODUCTO REAL MENOS VENDIDO: Outback Lager (5 u., $60.00).
--    - PRODUCTO ARROJADO POR EL JOIN INGENUO: Sir Rodney's Marmalade (30 u. infladas, $1,944.00) o Geitost ($400.00).
--
-- 3. En 1997 - Eastern:
--    - PRODUCTO REAL MENOS VENDIDO: Mishi Kobe Niku (16 u., $1,552.00) o Konbu ($232.80).
--    - PRODUCTO ARROJADO POR EL JOIN INGENUO: Valkoinen suklaa (50 u. infladas, $650.00).
--
-- CONCLUSIÓN: No corregir la multiplicidad de territorios produce reportes de negocio falsos
-- que inducirían a decisiones operativas completamente erradas.
WITH NaiveVentas AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        p.ProductName,
        SUM(od.Quantity) AS naive_unid,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS naive_ganancia,
        DENSE_RANK() OVER (PARTITION BY YEAR(o.OrderDate), r.RegionID ORDER BY SUM(od.Quantity) ASC) AS rnk
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN employees e ON o.EmployeeID = e.EmployeeID
    INNER JOIN employeeterritories et ON e.EmployeeID = et.EmployeeID
    INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    INNER JOIN region r ON t.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, p.ProductName
)
SELECT 
    anio, 
    RegionID, 
    GROUP_CONCAT(CONCAT(ProductName, ' (Unid. Falsas: ', naive_unid, ', $', naive_ganancia, ')') SEPARATOR '; ') AS productos_erroneos_join_ingenuo
FROM NaiveVentas
WHERE rnk = 1
GROUP BY anio, RegionID
ORDER BY anio, RegionID;


-- ===================================================================================
-- FASE 4: DEFINICIÓN DE CRITERIOS DE NEGOCIO Y MANEJO DE EMPATES
-- En analítica de retail, la expresión "el producto que menos se vendió" admite dos
-- definiciones legítimas que un ingeniero de bases de datos debe diferenciar:
--
-- Criterio A: Menor Volumen Físico de Demanda (Unidades Vendidas)
--   Fórmula: RANK() OVER (PARTITION BY Año, Región ORDER BY SUM(Quantity) ASC)
--   Prioriza los productos con menor movimiento de inventario / unidades colocadas.
--
-- Criterio B: Menor Ingreso Monetario Generado (Facturación / Ganancia Neta)
--   Fórmula: RANK() OVER (PARTITION BY Año, Región ORDER BY SUM(UnitPrice * Quantity * (1 - Discount)) ASC)
--   Prioriza los productos con menor recaudación económica.
--
-- El Problema de los Empates (Ties):
--   En varios períodos existen empates exactos en el primer lugar de menor venta:
--     - 1996 Eastern: Genen Shouyu (5 u.) y Laughing Lumberjack Lager (5 u.) tienen exactamente 5 unidades.
--     - 1997 Westerns: Laughing Lumberjack Lager (3 u.) y Uncle Bob's Organic Dried Pears (3 u.) tienen exactamente 3 unidades.
--   Regla de Ingeniería: Utilizar DENSE_RANK() = 1 y GROUP_CONCAT() para que la celda
--   muestre a TODOS los productos empatados, en lugar de un LIMIT 1 arbitrario que ocultaría datos reales.
-- ===================================================================================

-- 4.1 Identificación analítica de los productos menos vendidos bajo Criterio A (Unidades)
WITH VentasCorrectas AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        TRIM(r.RegionDescription) AS region,
        p.ProductID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription, p.ProductID, p.ProductName
),
RankedPorUnidades AS (
    SELECT 
        anio,
        RegionID,
        region,
        ProductID,
        ProductName,
        unidades_vendidas,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY unidades_vendidas ASC) AS rnk_unidades
    FROM VentasCorrectas
)
SELECT 
    anio,
    region,
    ProductID,
    ProductName,
    unidades_vendidas,
    ganancia_neta
FROM RankedPorUnidades
WHERE rnk_unidades = 1
ORDER BY anio, RegionID, ProductName;


-- 4.2 Identificación analítica de los productos menos vendidos bajo Criterio B (Ganancia Neta)
WITH VentasCorrectas AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        TRIM(r.RegionDescription) AS region,
        p.ProductID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription, p.ProductID, p.ProductName
),
RankedPorGanancia AS (
    SELECT 
        anio,
        RegionID,
        region,
        ProductID,
        ProductName,
        unidades_vendidas,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY ganancia_neta ASC) AS rnk_ganancia
    FROM VentasCorrectas
)
SELECT 
    anio,
    region,
    ProductID,
    ProductName,
    unidades_vendidas,
    ganancia_neta
FROM RankedPorGanancia
WHERE rnk_ganancia = 1
ORDER BY anio, RegionID, ProductName;


-- ===================================================================================
-- FASE 5: CONSTRUCCIÓN ITERATIVA DE LA MATRIZ PIVOTEADA (Pivot Table)
-- Para responder exactamente al requerimiento: "el año y las 4 regiones sean las columnas
-- y en la celda muestre los productos con su ganancia", se utiliza la técnica estándar
-- de pivoteo condicional en SQL (CASE WHEN + MAX() agrupado por Año).
-- ===================================================================================

-- 5.1 Paso 1 del Pivoteo: Consolidación del contenido de celda por Año y Región
-- Propósito: Generar una sola cadena formateada por cada intersección (Año, RegiónID)
-- conteniendo el nombre del producto y su ganancia entre paréntesis.
WITH VentasCorrectas AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, p.ProductName
),
Ranked AS (
    SELECT 
        anio,
        RegionID,
        ProductName,
        unidades_vendidas,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY unidades_vendidas ASC) AS rnk
    FROM VentasCorrectas
)
SELECT 
    anio,
    RegionID,
    GROUP_CONCAT(
        CONCAT(ProductName, ' ($', FORMAT(ganancia_neta, 2), ')')
        ORDER BY ProductName
        SEPARATOR '; '
    ) AS texto_celda
FROM Ranked
WHERE rnk = 1
GROUP BY anio, RegionID
ORDER BY anio, RegionID;


-- ===================================================================================
-- FASE 6: CONSULTAS FINALES (Entregables Oficiales del Encargo 2)
-- A continuación se presentan las soluciones maestras pivoteadas:
--
-- 6.1 CONSULTA PRINCIPAL EJECUTIVA (Criterio Unidades con Detalle Completo)
--     Muestra los productos con menor demanda en unidades, indicando en cada celda:
--     "Nombre Producto ($Ganancia, N u.)", resolviendo empates con separación limpia.
--
-- 6.2 CONSULTA FINAL FINANCIERA (Criterio Recaudación Monetaria)
--     Muestra los productos con menor facturación en dinero en cada región y año:
--     "Nombre Producto ($Ganancia)".
--
-- 6.3 CONSULTA FINAL ESTÁNDAR CONCISA
--     Muestra la versión directa con el formato estándar pedido en el enunciado:
--     "Nombre Producto ($Ganancia)" basado en unidades vendidas.
-- ===================================================================================

-- 6.1 CONSULTA PRINCIPAL EJECUTIVA (Master Query con Unidades y Ganancia)
-- Recomendada para máxima claridad ejecutiva (permite ver tanto las unidades mínimas como la ganancia).
WITH VentasProducto AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, p.ProductName
),
RankedPorUnidades AS (
    SELECT 
        anio,
        RegionID,
        ProductName,
        unidades_vendidas,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY unidades_vendidas ASC) AS rnk
    FROM VentasProducto
),
CeldasConsolidadas AS (
    SELECT 
        anio,
        RegionID,
        GROUP_CONCAT(
            CONCAT(ProductName, ' ($', FORMAT(ganancia_neta, 2), ', ', unidades_vendidas, ' u.)')
            ORDER BY ProductName
            SEPARATOR '; '
        ) AS contenido_celda
    FROM RankedPorUnidades
    WHERE rnk = 1
    GROUP BY anio, RegionID
)
SELECT 
    anio AS 'Año',
    MAX(CASE WHEN RegionID = 1 THEN contenido_celda END) AS 'Eastern',
    MAX(CASE WHEN RegionID = 2 THEN contenido_celda END) AS 'Westerns',
    MAX(CASE WHEN RegionID = 3 THEN contenido_celda END) AS 'Northern',
    MAX(CASE WHEN RegionID = 4 THEN contenido_celda END) AS 'Southern'
FROM CeldasConsolidadas
GROUP BY anio
ORDER BY anio ASC;


-- 6.2 CONSULTA FINAL FINANCIERA (Menor Recaudación / Facturación en Dólares)
WITH VentasProducto AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, p.ProductName
),
RankedPorGanancia AS (
    SELECT 
        anio,
        RegionID,
        ProductName,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY ganancia_neta ASC) AS rnk
    FROM VentasProducto
),
CeldasConsolidadas AS (
    SELECT 
        anio,
        RegionID,
        GROUP_CONCAT(
            CONCAT(ProductName, ' ($', FORMAT(ganancia_neta, 2), ')')
            ORDER BY ProductName
            SEPARATOR '; '
        ) AS contenido_celda
    FROM RankedPorGanancia
    WHERE rnk = 1
    GROUP BY anio, RegionID
)
SELECT 
    anio AS 'Año',
    MAX(CASE WHEN RegionID = 1 THEN contenido_celda END) AS 'Eastern',
    MAX(CASE WHEN RegionID = 2 THEN contenido_celda END) AS 'Westerns',
    MAX(CASE WHEN RegionID = 3 THEN contenido_celda END) AS 'Northern',
    MAX(CASE WHEN RegionID = 4 THEN contenido_celda END) AS 'Southern'
FROM CeldasConsolidadas
GROUP BY anio
ORDER BY anio ASC;


-- 6.3 CONSULTA FINAL ESTÁNDAR CONCISA (Entregable Literal del Encargo 2)
-- Estrictamente: Año y las 4 regiones como columnas, y en la celda: "Producto ($Ganancia)"
WITH VentasProducto AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, p.ProductName
),
RankedMenosVendidos AS (
    SELECT 
        anio,
        RegionID,
        ProductName,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY unidades_vendidas ASC) AS rnk
    FROM VentasProducto
),
CeldasMatriz AS (
    SELECT 
        anio,
        RegionID,
        GROUP_CONCAT(
            CONCAT(ProductName, ' ($', FORMAT(ganancia_neta, 2), ')')
            ORDER BY ProductName
            SEPARATOR '; '
        ) AS celda
    FROM RankedMenosVendidos
    WHERE rnk = 1
    GROUP BY anio, RegionID
)
SELECT 
    anio AS 'Año',
    MAX(CASE WHEN RegionID = 1 THEN celda END) AS 'Eastern',
    MAX(CASE WHEN RegionID = 2 THEN celda END) AS 'Westerns',
    MAX(CASE WHEN RegionID = 3 THEN celda END) AS 'Northern',
    MAX(CASE WHEN RegionID = 4 THEN celda END) AS 'Southern'
FROM CeldasMatriz
GROUP BY anio
ORDER BY anio ASC;


-- ===================================================================================
-- FASE 7: AUDITORÍA Y VALIDACIÓN CELDA POR CELDA (Sanity Check Forense)
-- Propósito: Auditar individualmente las 12 intersecciones de la matriz (3 años x 4 regiones)
-- para demostrar de manera concluyente que no existe ningún otro producto con menor venta
-- en la base de datos real.
-- ===================================================================================

WITH VentasProducto AS (
    SELECT 
        YEAR(o.OrderDate) AS anio,
        r.RegionID,
        TRIM(r.RegionDescription) AS region,
        p.ProductID,
        p.ProductName,
        SUM(od.Quantity) AS unidades_vendidas,
        ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS ganancia_neta
    FROM orders o
    INNER JOIN `order details` od ON o.OrderID = od.OrderID
    INNER JOIN products p ON od.ProductID = p.ProductID
    INNER JOIN (
        SELECT DISTINCT et.EmployeeID, t.RegionID
        FROM employeeterritories et
        INNER JOIN territories t ON et.TerritoryID = t.TerritoryID
    ) emp_reg ON o.EmployeeID = emp_reg.EmployeeID
    INNER JOIN region r ON emp_reg.RegionID = r.RegionID
    GROUP BY YEAR(o.OrderDate), r.RegionID, r.RegionDescription, p.ProductID, p.ProductName
),
Ranked AS (
    SELECT 
        anio,
        RegionID,
        region,
        ProductID,
        ProductName,
        unidades_vendidas,
        ganancia_neta,
        DENSE_RANK() OVER (PARTITION BY anio, RegionID ORDER BY unidades_vendidas ASC) AS rnk_unidades,
        MIN(unidades_vendidas) OVER (PARTITION BY anio, RegionID) AS min_unidades_de_la_region
    FROM VentasProducto
)
SELECT 
    anio AS 'Año Auditado',
    region AS 'Región',
    ProductName AS 'Producto Menos Vendido Confirmado',
    unidades_vendidas AS 'Unidades Reales',
    min_unidades_de_la_region AS 'Mínimo Absoluto Comprobado',
    CONCAT('$', FORMAT(ganancia_neta, 2)) AS 'Ganancia Verificada',
    CASE 
        WHEN unidades_vendidas = min_unidades_de_la_region THEN 'AUDITORÍA EXITOSA: MÍNIMO DEMOSTRADO'
        ELSE 'ERROR DE CÁLCULO'
    END AS 'Estado de Certificación'
FROM Ranked
WHERE rnk_unidades = 1
ORDER BY anio, RegionID, ProductName;
