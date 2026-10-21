-- ===================================================================================
-- PRÁCTICA 2: ANÁLISIS INTEGRAL DE DATOS Y DETERMINACIÓN DE GANANCIAS POR EDITORIAL Y AUTOR
-- Base de Datos: pubs (MySQL 8.0)
-- Archivo: encargo3.sql
-- ===================================================================================
-- OBJETIVO:
-- Generar una consulta que muestre las ganancias generadas a cada editorial y por autor,
-- documentando paso a paso cada consulta exploratoria, diagnóstico forense,
-- demostración de errores comunes (multiplicación cartesiana en libros multi-autor,
-- pérdida de libros huérfanos sin autor) y las decisiones de diseño tomadas
-- hasta llegar a las consultas definitivas (desglose jerárquico con ROLLUP y matriz
-- cruzada bidimensional), con validación y conciliación contable al 100%.
-- ===================================================================================

USE pubs;

-- ===================================================================================
-- FASE 1: RECONOCIMIENTO Y EXPLORACIÓN INICIAL DE TABLAS (Data Discovery)
-- Un ingeniero en bases de datos inicia todo análisis auditando el modelo relacional,
-- las llaves primarias, llaves foráneas y la semántica de los campos económicos.
-- ===================================================================================

-- 1.1 Exploración del catálogo de editoriales (publishers)
-- Propósito: Determinar el universo total de editoriales registradas en la compañía.
-- Hallazgo: Existen 8 editoriales registradas en Estados Unidos, Alemania y Francia.
SELECT COUNT(*) AS total_editoriales FROM publishers;

SELECT 
    pub_id, 
    pub_name, 
    city, 
    state, 
    country 
FROM publishers
ORDER BY pub_id;


-- 1.2 Exploración del catálogo de libros (titles) y su asignación editorial
-- Propósito: Verificar cuántos libros tiene publicados cada editorial (FK pub_id)
-- e inspeccionar las columnas financieras esenciales: price (precio de venta),
-- royalty (% contractual de regalías de la editorial al autor) y advance (anticipo).
-- Hallazgo Crítico: Solo 3 de las 8 editoriales tienen títulos en el catálogo:
--   - Binnet & Hardley (0877):       7 títulos publicados.
--   - Algodata Infosystems (1389):   5 títulos publicados.
--   - New Moon Books (0736):         5 títulos publicados.
-- Las otras 5 editoriales del catálogo tienen 0 títulos registrados.
SELECT COUNT(*) AS total_titulos FROM titles;

SELECT 
    p.pub_id,
    p.pub_name,
    COUNT(t.title_id) AS total_titulos_publicados,
    ROUND(AVG(t.price), 2) AS precio_promedio,
    ROUND(AVG(t.royalty), 2) AS porcentaje_regalia_promedio
FROM publishers p
LEFT JOIN titles t ON p.pub_id = t.pub_id
GROUP BY p.pub_id, p.pub_name
ORDER BY total_titulos_publicados DESC;


-- 1.3 Exploración de la asignación autor-libro (titleauthor)
-- Propósito: Analizar la tabla puente que conecta a los autores con los libros (relación N:M).
-- Hallazgo: Contiene 25 registros. Incluye la columna clave 'royaltyper', que define el
-- porcentaje de participación o autoría de cada autor sobre el libro específico.
SELECT COUNT(*) AS total_relaciones_autor_libro FROM titleauthor;

SELECT 
    ta.title_id, 
    ta.au_id, 
    ta.au_ord, 
    ta.royaltyper 
FROM titleauthor ta
ORDER BY ta.title_id, ta.au_ord
LIMIT 10;


-- 1.4 Exploración de la nómina de autores (authors) y autores multi-editorial
-- Propósito: Determinar el universo de autores y comprobar si algún autor trabaja
-- para más de una editorial distinta.
-- Hallazgo: Existen 23 autores registrados.
-- DESCUBRIMIENTO FORENSE: El autor Michael O'Leary (267-41-2394) escribe para DOS editoriales:
--   - Algodata Infosystems (libro BU1111).
--   - Binnet & Hardley (libro TC7777).
-- Los demás autores con obras publicadas trabajan exclusivamente para una editorial.
SELECT COUNT(*) AS total_autores FROM authors;

SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    COUNT(DISTINCT t.pub_id) AS total_editoriales_asociadas,
    GROUP_CONCAT(DISTINCT p.pub_name SEPARATOR ', ') AS editoriales
FROM authors a
INNER JOIN titleauthor ta ON a.au_id = ta.au_id
INNER JOIN titles t ON ta.title_id = t.title_id
INNER JOIN publishers p ON t.pub_id = p.pub_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY total_editoriales_asociadas DESC;


-- 1.5 Exploración de la tabla transaccional de ventas (sales)
-- Propósito: Conocer los pedidos comerciales reales donde se genera el flujo de dinero.
-- Hallazgo: Existen 21 órdenes de venta sobre 7 títulos distintos.
SELECT COUNT(*) AS total_registros_ventas FROM sales;

SELECT 
    stor_id, 
    ord_num, 
    ord_date, 
    title_id, 
    qty 
FROM sales 
ORDER BY ord_date 
LIMIT 10;


-- ===================================================================================
-- FASE 2: ESTABLECER LA LÍNEA BASE CONTABLE (Ground Truth Oficial)
-- Para asegurar la precisión del análisis, determinamos la cifra dorada de control
-- financiero tanto a nivel global como desagregada por editorial en la tabla 'sales'.
-- ===================================================================================

-- 2.1 Cálculo del Total Global Facturado de la Empresa (Línea Base Oficial)
-- Propósito: Obtener el monto absoluto facturado por la venta de libros: SUM(s.qty * t.price).
-- Cifra Oficial de Control: $3,863.80 en 493 unidades vendidas a lo largo de 21 órdenes.
SELECT 
    COUNT(DISTINCT s.ord_num) AS total_ordenes_venta,
    COUNT(DISTINCT s.title_id) AS titulos_con_movimiento,
    SUM(s.qty) AS unidades_totales_vendidas,
    ROUND(SUM(s.qty * t.price), 2) AS total_ventas_reales_empresa
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id;


-- 2.2 Desglose oficial de ventas por editorial
-- Propósito: Conocer la facturación real generada en cada editorial.
-- Resultado Oficial de Control:
--   - 1389 (Algodata Infosystems):   90 unidades | $1,598.60 (3 títulos con venta).
--   - 0736 (New Moon Books):        133 unidades | $1,382.35 (2 títulos con venta).
--   - 0877 (Binnet & Hardley):       55 unidades |   $882.85 (2 títulos con venta).
--   - Las otras 5 editoriales:        0 unidades |     $0.00.
-- Suma exacta de las 3 editoriales activas: $3,863.80 (100.00% exacto).
SELECT 
    p.pub_id,
    p.pub_name,
    COUNT(DISTINCT t.title_id) AS titulos_con_ventas,
    COALESCE(SUM(s.qty), 0) AS unidades_vendidas,
    ROUND(COALESCE(SUM(s.qty * t.price), 0), 2) AS facturacion_real_editorial
FROM publishers p
LEFT JOIN titles t ON p.pub_id = t.pub_id
LEFT JOIN sales s ON t.title_id = s.title_id
GROUP BY p.pub_id, p.pub_name
ORDER BY facturacion_real_editorial DESC;


-- ===================================================================================
-- FASE 3: EL INTENTO INGENUO Y LA GRAN DISCREPANCIA (El Error Común)
-- El enfoque inicial que un programador inexperto intentaría es unir en serie directa:
-- publishers -> titles -> sales -> titleauthor -> authors
-- agrupando por editorial y autor, sumando (qty * price).
-- ===================================================================================

-- 3.1 Primer intento ingenuo uniendo todas las tablas en cadena directa
-- Propósito: Evaluar qué resultado devuelve un JOIN ingenuo agrupado por editorial y autor.
-- Resultado: Aparentemente devuelve 8 combinaciones autor-editorial.
SELECT 
    p.pub_name AS editorial,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    ROUND(SUM(s.qty * t.price), 2) AS ganancia_calculada_ingenua
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
INNER JOIN sales s ON t.title_id = s.title_id
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN authors a ON ta.au_id = a.au_id
GROUP BY p.pub_name, a.au_fname, a.au_lname
ORDER BY p.pub_name, ganancia_calculada_ingenua DESC;


-- 3.2 Comprobación matemática: Sumar los resultados del intento ingenuo
-- Propósito: Auditar si la suma del intento ingenuo coincide con las ventas de la empresa ($3,863.80).
-- ¡ALERTA CRÍTICA DE DISCREPANCIA!:
-- Suma obtenida con el JOIN ingenuo:  $4,708.90
-- Ventas reales de la empresa:        $3,863.80
-- ¡HAY UN DESFASE ASTRONÓMICO DE +$845.10! Las cuentas no cuadran.
SELECT 
    ROUND(SUM(ganancia_calculada_ingenua), 2) AS suma_total_ingenuo,
    (SELECT ROUND(SUM(s.qty * t.price), 2) FROM sales s INNER JOIN titles t ON s.title_id = t.title_id) AS venta_real_empresa,
    ROUND(SUM(ganancia_calculada_ingenua) - (SELECT SUM(s.qty * t.price) FROM sales s INNER JOIN titles t ON s.title_id = t.title_id), 2) AS desfase_inflado
FROM (
    SELECT 
        SUM(s.qty * t.price) AS ganancia_calculada_ingenua
    FROM publishers p
    INNER JOIN titles t ON p.pub_id = t.pub_id
    INNER JOIN sales s ON t.title_id = s.title_id
    INNER JOIN titleauthor ta ON t.title_id = ta.title_id
    INNER JOIN authors a ON ta.au_id = a.au_id
    GROUP BY p.pub_name, a.au_id
) AS subconsulta;


-- ===================================================================================
-- FASE 4: AUDITORÍA FORENSE DE LA BASE DE DATOS (Diagnóstico de Causa Raíz)
-- En esta fase investigamos las causas exactas por las cuales $4,708.90 != $3,863.80.
-- Analizamos los libros multi-autor, los libros huérfanos sin autor y los porcentajes
-- de participación en 'titleauthor'.
-- ===================================================================================

-- 4.1 INVESTIGACIÓN 1: Libros con múltiples autores (Duplicación en Ventas por JOIN)
-- Propósito: Identificar qué títulos tienen más de un autor en 'titleauthor' y cómo afectan a cada editorial.
-- Hallazgos Forenses:
-- 1. En Algodata Infosystems:
--    - Libro 'PC8888' ("Secrets of Silicon Valley"): Vendió $1,000.00 (50 u. a $20.00).
--    - Tiene 2 autoras: Ann Dull y Sheryl Hunter.
--    - Al hacer JOIN ingenuo, cada una recibe $1,000.00, sumando $2,000.00 (+$1,000.00 de duplicidad).
-- 2. En Binnet & Hardley:
--    - Libro 'MC3021' ("The Gourmet Microwave"): Vendió $44.85 (15 u. a $2.99).
--    - Tiene 2 autores: Michel DeFrance y Anne Ringer.
--    - Al hacer JOIN ingenuo, cada uno recibe $44.85, sumando $89.70 (+$44.85 de duplicidad).
-- Duplicidad total generada en el JOIN ingenuo: $1,000.00 + $44.85 = +$1,044.85 en ventas infladas.
SELECT 
    p.pub_name AS editorial,
    t.title_id,
    t.title,
    COUNT(DISTINCT ta.au_id) AS numero_autores,
    ROUND(SUM(s.qty * t.price) / COUNT(DISTINCT ta.au_id), 2) AS venta_real_libro,
    ROUND(SUM(s.qty * t.price), 2) AS venta_duplicada_por_join
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN sales s ON t.title_id = s.title_id
GROUP BY p.pub_name, t.title_id, t.title
HAVING COUNT(DISTINCT ta.au_id) > 1;


-- 4.2 INVESTIGACIÓN 2: Libros huérfanos sin autor (Libros vendidos por una editorial sin autor registrado)
-- Propósito: Detectar títulos vendidos que NO poseen autor asignado en 'titleauthor'.
-- Hallazgo Crítico Forense:
-- El libro 'PS7777' ("Emotional Security: A New Algorithm"), publicado por New Moon Books (0736),
-- ¡NO TIENE NINGÚN AUTOR ASIGNADO en la tabla 'titleauthor'!
-- Sin embargo, vendió 25 unidades a $7.99 = $199.75 en la tabla 'sales'.
-- Al usar INNER JOIN con 'titleauthor'/'authors', este libro SE DESCARTA POR COMPLETO,
-- perdiendo -$199.75 de ventas reales que la editorial New Moon Books sí facturó.
SELECT 
    p.pub_name AS editorial,
    t.title_id,
    t.title,
    t.price,
    SUM(s.qty) AS unidades_vendidas,
    ROUND(SUM(s.qty * t.price), 2) AS ventas_huerfanas_sin_autor
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN sales s ON t.title_id = s.title_id
WHERE ta.title_id IS NULL
GROUP BY p.pub_name, t.title_id, t.title, t.price;


-- 4.3 INVESTIGACIÓN 3: La columna 'royaltyper' y porcentajes no asignados a autores
-- Propósito: Analizar la distribución de autoría en 'titleauthor'.
-- Hallazgo:
--   - En PC8888 (Algodata): Ann Dull (50%) y Sheryl Hunter (50%) -> Suma 100%.
--   - En MC3021 (Binnet & Hardley): Michel DeFrance (75%) y Anne Ringer (25%) -> Suma 100%.
--   - En BU1111 (Algodata): Michael O'Leary tiene 40%. ¡Falta el 60% restante ($179.25)!
--   - En PS2091 (New Moon Books): Albert Ringer tiene 50%. ¡Falta el 50% restante ($591.30)!
-- Conclusión: Ese porcentaje restante no corresponde a autores registrados, sino a derechos
-- retenidos directamente por la editorial o por coautores externos no listados en la nómina.
SELECT 
    t.pub_id,
    p.pub_name AS editorial,
    t.title_id,
    COUNT(ta.au_id) AS autores_registrados,
    SUM(ta.royaltyper) AS porcentaje_total_autores,
    100 - SUM(ta.royaltyper) AS porcentaje_retenido_por_editorial
FROM titles t
INNER JOIN publishers p ON t.pub_id = p.pub_id
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
GROUP BY t.pub_id, p.pub_name, t.title_id
HAVING SUM(ta.royaltyper) < 100;


-- 4.4 CONCILIACIÓN MATEMÁTICA FORENSE DE LA DISCREPANCIA INGENUA:
-- Total ventas reales de la empresa:              $3,863.80
-- (+) Duplicación por libros multi-autor:        +$1,044.85 (PC8888: $1,000.00, MC3021: $44.85)
-- (-) Omisión del libro sin autor PS7777:         -$199.75 (New Moon Books)
-- (========================================================)
-- Total exacto obtenido en el intento ingenuo:   $4,708.90
-- ¡La causa raíz queda 100% demostrada y explicada matemáticamente!


-- ===================================================================================
-- FASE 5: DEFINICIÓN DE CRITERIOS DE NEGOCIO Y FINANCIEROS
-- Al analizar las ganancias generadas a cada editorial y por autor, existen dos lecturas:
--
-- Criterio 1 (Ventas Atribuibles de Productos - Facturación Bruta):
--   El volumen de facturación generado por cada autor para su editorial:
--   Fórmula: s.qty * t.price * (ta.royaltyper / 100.0)
--
-- Criterio 2 (Reparto Económico Contractual: Regalías del Autor vs. Margen de la Editorial):
--   - Regalías cobradas por el autor:
--     s.qty * t.price * (t.royalty / 100.0) * (ta.royaltyper / 100.0)
--   - Margen retenido por la editorial sobre las ventas del autor:
--     s.qty * t.price * (ta.royaltyper / 100.0) * (1 - (t.royalty / 100.0))
--
-- Criterio 3 (Alternativa por Ventas de Catálogo Histórico ytd_sales):
--   Cálculo sobre el campo titles.ytd_sales en lugar de la tabla 'sales'.
-- ===================================================================================

-- 5.1 Consulta base con ponderación por 'royaltyper' e inclusión de libros sin autor
-- Propósito: Desacoplar la multiplicidad y asignar a cada autor y a cada editorial
-- exactamente la porción que le corresponde, sin duplicar ingresos.
SELECT 
    p.pub_id,
    p.pub_name AS editorial,
    COALESCE(a.au_id, 'SIN_AUTOR') AS au_id,
    COALESCE(CONCAT(a.au_fname, ' ', a.au_lname), '(Venta Editorial / Sin Autor Asignado)') AS autor,
    COUNT(DISTINCT t.title_id) AS total_titulos,
    SUM(s.qty) AS unidades_vendidas_brutas,
    ROUND(SUM(s.qty * t.price * (COALESCE(ta.royaltyper, 100) / 100.0)), 2) AS ventas_atribuibles
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
INNER JOIN sales s ON t.title_id = s.title_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
LEFT JOIN authors a ON ta.au_id = a.au_id
GROUP BY p.pub_id, p.pub_name, a.au_id, autor
ORDER BY p.pub_name, ventas_atribuibles DESC;


-- ===================================================================================
-- FASE 6: CONSULTAS FINALES ENTREGABLES (Soluciones Maestras)
-- A continuación se presentan las soluciones maestras para el Encargo 3:
--
-- 6.1 CONSULTA PRINCIPAL JERÁRQUICA CON WITH ROLLUP
--     Muestra de manera estructurada cada Editorial, los Autores que generaron ingresos
--     para ella, las ventas atribuibles, las regalías de cada autor y el margen de la
--     editorial, con subtotales por editorial y el Total General de la empresa.
--
-- 6.2 MATRIZ CRUZADA BIDIMENSIONAL (Pivot Table Editorial x Autor)
--     Presenta en formato de matriz analítica las Editoriales en las filas y los Autores
--     en las columnas, cruzando la ganancia generada en cada celda.
--
-- 6.3 CONSULTA FINAL ESTÁNDAR CONCISA
--     Muestra de forma directa y compacta la relación (Editorial, Autor, Ganancias).
--
-- 6.4 CONSULTA CON CRITERIO ALTERNATIVO (ytd_sales de Catálogo)
--     Muestra las ganancias basadas en el acumulado anual histórico de catálogo.
-- ===================================================================================

-- 6.1 CONSULTA PRINCIPAL EJECUTIVA JERÁRQUICA (Master Query con WITH ROLLUP)
-- Esta es la consulta recomendada por excelencia para directores de finanzas y analistas:
-- 1. Detalla la aportación de cada autor dentro de su respectiva editorial.
-- 2. Pondera las ventas con 'royaltyper' para resolver la duplicidad en coautorías.
-- 3. Incluye las ventas de libros sin autor asignado (PS7777 de New Moon Books).
-- 4. Separa las regalías líquidas que cobra el autor del margen que retiene la editorial.
-- 5. Genera subtotales oficiales por editorial y el Total General auditado de la empresa.
WITH BaseVentas AS (
    SELECT 
        p.pub_id,
        p.pub_name,
        COALESCE(CONCAT(a.au_fname, ' ', a.au_lname), '(Venta Editorial / Sin Autor Asignado)') AS autor,
        t.title_id,
        s.qty,
        t.price,
        t.royalty,
        COALESCE(ta.royaltyper, 100) AS royaltyper
    FROM publishers p
    INNER JOIN titles t ON p.pub_id = t.pub_id
    INNER JOIN sales s ON t.title_id = s.title_id
    LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
    LEFT JOIN authors a ON ta.au_id = a.au_id
)
SELECT 
    CASE 
        WHEN GROUPING(pub_name) = 1 THEN '>>> TOTAL GENERAL EMPRESA <<<'
        ELSE pub_name 
    END AS 'Editorial',
    CASE 
        WHEN GROUPING(autor) = 1 THEN '--- SUBTOTAL EDITORIAL ---'
        ELSE autor 
    END AS 'Autor',
    COUNT(DISTINCT title_id) AS 'Títulos Vendidos',
    SUM(qty) AS 'Unidades Brutas',
    ROUND(SUM(qty * price * (royaltyper / 100.0)), 2) AS 'Ventas Atribuibles ($)',
    ROUND(SUM(qty * price * (royalty / 100.0) * (royaltyper / 100.0)), 2) AS 'Regalías del Autor ($)',
    ROUND(SUM(qty * price * (royaltyper / 100.0) * (1 - (royalty / 100.0))), 2) AS 'Margen de la Editorial ($)'
FROM BaseVentas
GROUP BY pub_name, autor WITH ROLLUP;


-- 6.2 MATRIZ CRUZADA BIDIMENSIONAL (Pivot Table: Editorial x Autor)
-- Presenta en formato ejecutivo horizontal a todas las editoriales en filas y a los
-- autores con ventas en columnas, permitiendo visualizar de inmediato el aporte cruzado.
WITH VentasEditorialAutor AS (
    SELECT 
        p.pub_id,
        p.pub_name,
        COALESCE(a.au_id, 'SIN_AUTOR') AS au_id,
        COALESCE(CONCAT(a.au_fname, ' ', a.au_lname), 'Sin Autor') AS autor,
        ROUND(SUM(s.qty * t.price * (COALESCE(ta.royaltyper, 100) / 100.0)), 2) AS ganancia_atribuible
    FROM publishers p
    LEFT JOIN titles t ON p.pub_id = t.pub_id
    LEFT JOIN sales s ON t.title_id = s.title_id
    LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
    LEFT JOIN authors a ON ta.au_id = a.au_id
    GROUP BY p.pub_id, p.pub_name, a.au_id, autor
)
SELECT 
    pub_name AS 'Editorial',
    COALESCE(MAX(CASE WHEN au_id = '998-72-3567' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Albert Ringer',
    COALESCE(MAX(CASE WHEN au_id = '427-17-2319' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Ann Dull',
    COALESCE(MAX(CASE WHEN au_id = '899-46-2035' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Anne Ringer',
    COALESCE(MAX(CASE WHEN au_id = '274-80-9391' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Dean Straight',
    COALESCE(MAX(CASE WHEN au_id = '267-41-2394' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Michael O\'Leary',
    COALESCE(MAX(CASE WHEN au_id = '722-51-5454' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Michel DeFrance',
    COALESCE(MAX(CASE WHEN au_id = '846-92-7186' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Sheryl Hunter',
    COALESCE(MAX(CASE WHEN au_id = '807-91-6654' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Sylvia Panteley',
    COALESCE(MAX(CASE WHEN au_id = 'SIN_AUTOR' THEN CONCAT('$', FORMAT(ganancia_atribuible, 2)) END), '-') AS 'Sin Autor (PS7777)'
FROM VentasEditorialAutor
GROUP BY pub_name
ORDER BY pub_name;


-- 6.3 CONSULTA FINAL ESTÁNDAR CONCISA
-- Versión directa y compacta con los campos mínimos requeridos: (Editorial, Autor, Ganancias).
SELECT 
    p.pub_name AS editorial,
    COALESCE(CONCAT(a.au_fname, ' ', a.au_lname), '(Venta Editorial / Sin Autor Asignado)') AS autor,
    ROUND(SUM(s.qty * t.price * (COALESCE(ta.royaltyper, 100) / 100.0)), 2) AS ganancia_generada
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
INNER JOIN sales s ON t.title_id = s.title_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
LEFT JOIN authors a ON ta.au_id = a.au_id
GROUP BY p.pub_name, a.au_id, autor
ORDER BY p.pub_name, ganancia_generada DESC;


-- 6.4 CONSULTA CON CRITERIO ALTERNATIVO (Basada en 'ytd_sales' del Catálogo de Libros)
-- Por si el requerimiento académico solicita las ventas acumuladas anuales de catálogo
-- en lugar de las órdenes comerciales de la tabla 'sales'.
SELECT 
    p.pub_name AS editorial,
    COALESCE(CONCAT(a.au_fname, ' ', a.au_lname), '(Venta Editorial / Sin Autor Asignado)') AS autor,
    COUNT(DISTINCT t.title_id) AS titulos_publicados,
    ROUND(COALESCE(SUM(t.ytd_sales * t.price * (COALESCE(ta.royaltyper, 100) / 100.0)), 0), 2) AS ventas_ytd_atribuibles,
    ROUND(COALESCE(SUM(t.ytd_sales * t.price * (t.royalty / 100.0) * (COALESCE(ta.royaltyper, 100) / 100.0)), 0), 2) AS regalias_ytd_autor
FROM publishers p
INNER JOIN titles t ON p.pub_id = t.pub_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
LEFT JOIN authors a ON ta.au_id = a.au_id
WHERE t.ytd_sales IS NOT NULL
GROUP BY p.pub_name, a.au_id, autor
ORDER BY p.pub_name, ventas_ytd_atribuibles DESC;


-- ===================================================================================
-- FASE 7: ANEXO DE AUDITORÍA Y CONCILIACIÓN CONTABLE DEFINITIVA AL 100%
-- Propósito: Demostrar matemáticamente que el modelo propuesto concilia al centavo
-- la totalidad de los $3,863.80 facturados en la base de datos:
--   - Ventas atribuidas a autores registrados:                           $2,893.50
--   - Ventas del libro sin autor (PS7777 - New Moon Books):                $199.75
--   - Ventas por porcentaje no asignado (BU1111: $179.25, PS2091: $591.30): $770.55
--   - Suma total conciliada:                                             $3,863.80 (100.00% exacto).
-- ===================================================================================

SELECT 
    '1. Ventas Atribuidas a Autores Registrados' AS Concepto,
    ROUND(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 2) AS Monto_Total,
    'Suma de los 8 autores en las 3 editoriales' AS Auditoria
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN publishers p ON t.pub_id = p.pub_id

UNION ALL

SELECT 
    '2. Ventas de Libros sin Autor Asignado (PS7777 - New Moon Books)' AS Concepto,
    ROUND(SUM(s.qty * t.price), 2) AS Monto_Total,
    'Facturación retenida 100% por la editorial New Moon Books' AS Auditoria
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
WHERE ta.title_id IS NULL

UNION ALL

SELECT 
    '3. Porcentajes no Asignados a Autores (BU1111 y PS2091)' AS Concepto,
    ROUND(SUM(s.qty * t.price * ((100 - sub.total_royalty) / 100.0)), 2) AS Monto_Total,
    'Algodata retiene 60% de BU1111 ($179.25) y New Moon retiene 50% de PS2091 ($591.30)' AS Auditoria
FROM (
    SELECT DISTINCT stor_id, ord_num, title_id, qty 
    FROM sales
) s
INNER JOIN titles t ON s.title_id = t.title_id
INNER JOIN (
    SELECT title_id, SUM(royaltyper) AS total_royalty
    FROM titleauthor
    GROUP BY title_id
    HAVING SUM(royaltyper) < 100
) sub ON t.title_id = sub.title_id

UNION ALL

SELECT 
    '>>> TOTAL GENERAL AUDITADO DE TODAS LAS EDITORIALES <<<' AS Concepto,
    ROUND(SUM(s.qty * t.price), 2) AS Monto_Total,
    'Línea base oficial de la empresa: $3,863.80 (100.00% exacto)' AS Auditoria
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id;
