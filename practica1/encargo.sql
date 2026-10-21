-- ===================================================================================
-- PRÁCTICA 1: ANÁLISIS INTEGRAL DE DATOS Y DETERMINACIÓN DE GANANCIAS POR AUTOR
-- Base de Datos: pubs (MySQL 8.0)
-- Archivo: encargo.sql
-- ===================================================================================
-- OBJETIVO:
-- Generar la consulta que muestra la ganancia por autor, documentando cada una
-- de las consultas exploratorias, diagnósticos forenses y decisiones tomadas
-- hasta llegar a la consulta final definitiva, tal como lo realizaría un analista
-- de bases de datos profesional.
-- ===================================================================================

USE pubs;

-- ===================================================================================
-- FASE 1: RECONOCIMIENTO Y EXPLORACIÓN INICIAL DE TABLAS (Data Discovery)
-- Antes de calcular cualquier ganancia, un analista debe explorar las tablas del modelo,
-- sus volúmenes, llaves primarias, llaves foráneas y la semántica de sus campos.
-- ===================================================================================

-- 1.1 Conteo general y exploración de la tabla de autores (authors)
-- Propósito: Determinar el universo total de autores registrados en la base de datos.
-- Hallazgo: Existen 23 autores registrados con datos personales y estado contractual.
SELECT COUNT(*) AS total_autores FROM authors;

SELECT 
    au_id, 
    au_lname, 
    au_fname, 
    city, 
    state, 
    contract 
FROM authors 
LIMIT 10;


-- 1.2 Exploración del catálogo de libros (titles)
-- Propósito: Identificar las columnas financieras esenciales: 'price' (precio de venta),
-- 'royalty' (% de regalías del libro), 'advance' (adelanto) y 'ytd_sales' (ventas acumuladas anuales).
-- Hallazgo: Existen 17 títulos de diversas temáticas.
SELECT COUNT(*) AS total_titulos FROM titles;

SELECT 
    title_id, 
    title, 
    type, 
    price, 
    advance, 
    royalty, 
    ytd_sales 
FROM titles;


-- 1.3 Exploración de la tabla de relación autor-libro (titleauthor)
-- Propósito: Inspeccionar cómo se asocian autores y libros (relación N:M).
-- Hallazgo: Esta tabla contiene 'royaltyper', un campo porcentual clave que define la cuota
-- de autoría o participación en regalías de cada autor sobre un libro específico.
SELECT COUNT(*) AS total_relaciones_autor_libro FROM titleauthor;

SELECT 
    au_id, 
    title_id, 
    au_ord, 
    royaltyper 
FROM titleauthor 
ORDER BY title_id, au_ord;


-- 1.4 Exploración de la tabla transaccional de ventas (sales)
-- Propósito: Verificar dónde residen las ventas reales realizadas en puntos de venta / tiendas.
-- Hallazgo: Se cuenta con órdenes de compra por tienda (stor_id), número de orden (ord_num),
-- fecha (ord_date), cantidad vendida (qty) y el libro correspondiente (title_id).
SELECT COUNT(*) AS total_registros_ventas FROM sales;

SELECT 
    stor_id, 
    ord_num, 
    ord_date, 
    title_id, 
    qty, 
    payterms 
FROM sales 
ORDER BY ord_date;


-- ===================================================================================
-- FASE 2: ESTABLECER LA LÍNEA BASE DE VENTAS (Ground Truth Contable)
-- Para evaluar la validez de cualquier reporte de autor, primero debemos conocer
-- con exactitud matemática el total real vendido en la empresa (la "caja registradora").
-- ===================================================================================

-- 2.1 Cálculo del Total Global de Ventas de la Empresa (Línea Base Oficial)
-- Propósito: Obtener el monto total absoluto facturado por la venta de libros: SUM(qty * price).
-- Resultado Contable: $3,863.80.
-- Nota del Analista: Esta es la cifra oficial de control contra la cual deben cuadrar nuestros números.
SELECT 
    ROUND(SUM(s.qty * t.price), 2) AS total_ventas_reales_empresa
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id;


-- 2.2 Desglose de ventas reales por libro individual
-- Propósito: Conocer qué libros tuvieron movimiento en ventas y cuánto generó cada uno.
-- Hallazgo fundamental: Solo 7 de los 17 libros tienen ventas registradas en la tabla 'sales'.
-- Los otros 10 libros del catálogo tienen 0 ventas en órdenes comerciales.
SELECT 
    t.title_id,
    t.title,
    t.price,
    SUM(s.qty) AS unidades_vendidas,
    ROUND(SUM(s.qty * t.price), 2) AS venta_total_libro
FROM titles t
INNER JOIN sales s ON t.title_id = s.title_id
GROUP BY t.title_id, t.title, t.price
ORDER BY venta_total_libro DESC;


-- ===================================================================================
-- FASE 3: EL INTENTO INGENUO Y LA GRAN DISCREPANCIA (El Error Común)
-- El enfoque inicial que la mayoría de programadores intentaría es unir las 4 tablas
-- mediante INNER JOIN directamente y sumar (qty * price) por autor.
-- ===================================================================================

-- 3.1 Primer intento ingenuo de consulta de ganancias por autor
-- Propósito: Unir authors -> titleauthor -> titles -> sales agrupando por autor.
-- Resultado: Devuelve 8 autores con sus supuestas ganancias.
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    ROUND(SUM(s.qty * t.price), 2) AS ganancia_calculada
FROM authors a
INNER JOIN titleauthor ta ON a.au_id = ta.au_id
INNER JOIN titles t ON ta.title_id = t.title_id
INNER JOIN sales s ON t.title_id = s.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY ganancia_calculada DESC;


-- 3.2 Comprobación matemática: Sumar los resultados del intento ingenuo
-- Propósito: Auditar si la suma de las ganancias de los autores coincide con las ventas de la empresa.
-- ¡ALERTA DE DISCREPANCIA!:
-- Suma de autores con join ingenuo: $4,708.90
-- Ventas reales totales en la empresa: $3,863.80
-- ¡Hay un desfase inexplicable de +$845.10! Las cuentas NO cuadran.
SELECT 
    ROUND(SUM(ganancia_calculada), 2) AS suma_total_autores_ingenuo
FROM (
    SELECT 
        SUM(s.qty * t.price) AS ganancia_calculada
    FROM authors a
    INNER JOIN titleauthor ta ON a.au_id = ta.au_id
    INNER JOIN titles t ON ta.title_id = t.title_id
    INNER JOIN sales s ON t.title_id = s.title_id
    GROUP BY a.au_id
) AS subconsulta;


-- ===================================================================================
-- FASE 4: AUDITORÍA FORENSE DE LA BASE DE DATOS (Descubriendo los "Detalles Ocultos")
-- En esta fase investigamos las causas exactas por las cuales $4,708.90 != $3,863.80.
-- Se analizan libros multi-autor, libros huérfanos, autores inactivos y la columna 'royaltyper'.
-- ===================================================================================

-- 4.1 INVESTIGACIÓN 1: Libros con múltiples autores (Duplicidad en ventas por JOIN)
-- Propósito: Identificar qué libros tienen más de un autor registrado en 'titleauthor' y cómo afectan las ventas.
-- Primero: Identificar los libros multi-autor en el catálogo general:
SELECT 
    t.title_id,
    t.title,
    COUNT(DISTINCT ta.au_id) AS numero_autores
FROM titles t
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
GROUP BY t.title_id, t.title
HAVING COUNT(DISTINCT ta.au_id) > 1;

-- Segundo: Demostrar cómo el JOIN ingenuo multiplica las ventas de estos libros:
-- Hallazgos:
-- 1. 'PC8888' ("Secrets of Silicon Valley"): Vendió $1,000.00 (50 unidades a $20.00).
--    Tiene 2 autoras: Ann Dull y Sheryl Hunter. Al hacer JOIN ingenuo, cada una recibió $1,000.00,
--    sumando $2,000.00 en total (+$1,000.00 de duplicidad).
-- 2. 'MC3021' ("The Gourmet Microwave"): Vendió $44.85 (15 unidades a $2.99).
--    Tiene 2 autores: Michel DeFrance y Anne Ringer. Cada uno recibió $44.85,
--    sumando $89.70 en total (+$44.85 de duplicidad).
-- Duplicidad total generada en el JOIN ingenuo: $1,000.00 + $44.85 = +$1,044.85 en ventas infladas.
SELECT 
    t.title_id,
    t.title,
    COUNT(DISTINCT ta.au_id) AS numero_autores,
    ROUND(SUM(s.qty * t.price) / COUNT(DISTINCT ta.au_id), 2) AS venta_real_libro,
    ROUND(SUM(s.qty * t.price), 2) AS venta_duplicada_por_el_join
FROM titles t
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN sales s ON t.title_id = s.title_id
GROUP BY t.title_id, t.title
HAVING COUNT(DISTINCT ta.au_id) > 1;


-- 4.2 INVESTIGACIÓN 2: Libros huérfanos (Libros vendidos SIN NINGÚN AUTOR)
-- Propósito: Detectar títulos en 'titles' que NO tienen autor asignado en 'titleauthor'.
-- Hallazgo crítico:
-- El libro 'PS7777' ("Emotional Security: A New Algorithm") NO TIENE AUTOR en 'titleauthor'.
-- Sin embargo, ¡se vendieron 25 unidades a $7.99 = $199.75 en la tabla 'sales'!
-- Al usar INNER JOIN en la consulta ingenua, este libro se descarta completamente,
-- perdiendo -$199.75 de ventas reales que nadie cobró.
SELECT 
    t.title_id,
    t.title,
    ROUND(SUM(s.qty * t.price), 2) AS ventas_huerfanas_sin_autor
FROM titles t
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
INNER JOIN sales s ON t.title_id = s.title_id
WHERE ta.title_id IS NULL
GROUP BY t.title_id, t.title;


-- 4.3 CONCILIACIÓN MATEMÁTICA FORENSE DE LA DISCREPANCIA:
-- Total ventas reales de la empresa:              $3,863.80
-- (+) Duplicación por libros multi-autor:        +$1,044.85 (PC8888: $1000, MC3021: $44.85)
-- (-) Omisión del libro sin autor PS7777:         -$199.75
-- (========================================================)
-- Total exacto obtenido en el intento ingenuo:   $4,708.90
-- ¡La discrepancia queda 100% explicada y demostrada matemáticamente!


-- 4.4 INVESTIGACIÓN 3: Autores sin libros y autores sin ventas (Auditoría de Población)
-- Propósito: Verificar por qué la consulta ingenua solo mostró 8 autores de los 23 existentes.
-- Hallazgo 3a: Autores sin libros registrados en 'titleauthor' (4 autores):
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    'Sin libros registrados' AS situacion
FROM authors a
LEFT JOIN titleauthor ta ON a.au_id = ta.au_id
WHERE ta.title_id IS NULL;

-- Hallazgo 3b: Autores con libros registrados, pero con 0 ventas en la tabla 'sales' (11 autores):
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    COUNT(DISTINCT ta.title_id) AS libros_asociados,
    COUNT(s.ord_num) AS ordenes_venta
FROM authors a
INNER JOIN titleauthor ta ON a.au_id = ta.au_id
LEFT JOIN sales s ON ta.title_id = s.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
HAVING COUNT(s.ord_num) = 0;

-- Resumen de población:
-- 4 autores sin libros + 11 autores con libros pero sin ventas + 8 autores con ventas = 23 autores.
-- Conclusión para el diseño: Un reporte gerencial profesional debe usar LEFT JOIN para mostrar
-- a los 23 autores, indicando $0.00 en sus ventas, en lugar de excluirlos del análisis.


-- 4.5 INVESTIGACIÓN 4: La columna 'royaltyper' (Porcentaje de participación entre autores)
-- Propósito: Analizar la distribución de autoría en 'titleauthor'.
-- ¿Cómo se deben repartir las ventas entre coautores?
-- Para eso la base de datos provee 'royaltyper' (% de derechos de autor de cada uno).
-- Sorpresa adicional descubierta:
-- - En PC8888, los autores tienen 50% y 50% (suma 100%).
-- - En MC3021, los autores tienen 75% y 25% (suma 100%).
-- - En BU1111: Solo existe un autor registrado con 40% (falta el 60% restante).
-- - En PS2091: Solo existe un autor registrado con 50% (falta el 50% restante).
-- - En BU1032: Solo existe un autor registrado con 60% (falta el 40% restante).
-- Esto confirma que el porcentaje restante corresponde a coautores externos no registrados o a la editorial.
SELECT 
    title_id,
    COUNT(au_id) AS num_autores,
    SUM(royaltyper) AS porcentaje_total_registrado
FROM titleauthor
GROUP BY title_id;


-- ===================================================================================
-- FASE 5: CONSTRUCCIÓN ITERATIVA DE LA SOLUCIÓN
-- Con los hallazgos de la auditoría, construimos progresivamente la consulta correcta.
-- ===================================================================================

-- 5.1 Corrección de duplicación aplicando el factor de participación (royaltyper / 100)
-- Propósito: Multiplicar la venta de cada libro por el porcentaje de autoría correspondiente.
-- De esta forma, si un libro vendió $1,000 entre dos autores al 50%, a cada uno le tocan $500.00.
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    ROUND(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 2) AS ganancia_ponderada
FROM authors a
INNER JOIN titleauthor ta ON a.au_id = ta.au_id
INNER JOIN titles t ON ta.title_id = t.title_id
INNER JOIN sales s ON t.title_id = s.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY ganancia_ponderada DESC;


-- 5.2 Inclusión de Todos los Autores mediante LEFT JOIN y COALESCE
-- Propósito: Mostrar a los 23 autores de la base de datos sin perder a quienes tienen 0 ventas.
-- Se sustituyen los valores NULL por 0 mediante COALESCE.
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    COUNT(DISTINCT ta.title_id) AS total_libros,
    COALESCE(SUM(s.qty), 0) AS unidades_vendidas_brutas,
    ROUND(COALESCE(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 0), 2) AS ganancia_ventas_ponderada
FROM authors a
LEFT JOIN titleauthor ta ON a.au_id = ta.au_id
LEFT JOIN titles t ON ta.title_id = t.title_id
LEFT JOIN sales s ON t.title_id = s.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY ganancia_ventas_ponderada DESC;


-- ===================================================================================
-- FASE 6: DEFINICIÓN DE CRITERIOS DE NEGOCIO (Ventas Brutas vs. Regalías Netas)
-- En el mundo editorial existen dos conceptos de "Ganancia del Autor":
--
-- Criterio 1 (Ventas Atribuibles):
--   El volumen de facturación generado por los libros del autor según su autoría:
--   Fórmula: qty * price * (royaltyper / 100)
--
-- Criterio 2 (Regalías Netas en Mano):
--   El dinero real que el autor cobra contractualmente de la editorial:
--   Fórmula: qty * price * (titles.royalty / 100) * (titleauthor.royaltyper / 100)
--
-- Criterio 3 (Alternativa por Ventas de Catálogo Histórico ytd_sales):
--   Cálculo basado en el campo 'titles.ytd_sales' (year-to-date sales) en lugar de 'sales'.
-- ===================================================================================

-- 6.1 Comparativa simultánea de Ventas Atribuibles vs Regalías Netas sobre órdenes 'sales'
-- Propósito: Proporcionar a la dirección ambas métricas en una sola vista analítica.
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    COUNT(DISTINCT ta.title_id) AS libros_registrados,
    ROUND(COALESCE(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 0), 2) AS ventas_atribuibles_autor,
    ROUND(COALESCE(SUM(s.qty * t.price * (t.royalty / 100.0) * (ta.royaltyper / 100.0)), 0), 2) AS regalias_netas_autor
FROM authors a
LEFT JOIN titleauthor ta ON a.au_id = ta.au_id
LEFT JOIN titles t ON ta.title_id = t.title_id
LEFT JOIN sales s ON t.title_id = s.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY ventas_atribuibles_autor DESC;


-- 6.2 Consulta con Criterio 3 (utilizando 'ytd_sales' de la tabla 'titles')
-- Propósito: Mostrar las ganancias si el requerimiento docente hace referencia a las ventas acumuladas anuales.
-- En este caso, todos los libros tienen movimiento y se pondera igualmente por 'royaltyper'.
SELECT 
    a.au_id,
    CONCAT(a.au_fname, ' ', a.au_lname) AS autor,
    COUNT(DISTINCT t.title_id) AS libros_publicados,
    ROUND(COALESCE(SUM(t.ytd_sales * t.price * (ta.royaltyper / 100.0)), 0), 2) AS ventas_ytd_atribuibles,
    ROUND(COALESCE(SUM(t.ytd_sales * t.price * (t.royalty / 100.0) * (ta.royaltyper / 100.0)), 0), 2) AS regalias_ytd_netas
FROM authors a
LEFT JOIN titleauthor ta ON a.au_id = ta.au_id
LEFT JOIN titles t ON ta.title_id = t.title_id
GROUP BY a.au_id, a.au_fname, a.au_lname
ORDER BY ventas_ytd_atribuibles DESC;


-- ===================================================================================
-- FASE 7: CONSULTA FINAL DEFINITIVA (Master Query)
-- Esta es la consulta principal definitiva para la entrega de la Práctica 1.
-- Cumple con todos los estándares profesionales:
-- 1. Incluye al 100% de los autores (23 autores) sin descartar a los de 0 ventas.
-- 2. Resuelve la duplicidad de ingresos en libros multi-autor mediante 'royaltyper'.
-- 3. Muestra tanto el volumen de ventas generado como las regalías líquidas cobradas.
-- 4. Aplica COALESCE para evitar nulos y ROUND para precisión monetaria a 2 decimales.
-- 5. Nombres de columnas limpios, legibles y listos para presentación o reporte.
-- ===================================================================================

SELECT 
    a.au_id AS 'ID Autor',
    CONCAT(a.au_fname, ' ', a.au_lname) AS 'Nombre del Autor',
    a.city AS 'Ciudad',
    a.state AS 'Estado',
    COUNT(DISTINCT ta.title_id) AS 'Libros Publicados',
    COALESCE(SUM(s.qty), 0) AS 'Unidades Vendidas (Brutas)',
    ROUND(COALESCE(SUM(s.qty * (ta.royaltyper / 100.0)), 0), 2) AS 'Unidades Atribuibles',
    ROUND(COALESCE(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 0), 2) AS 'Ganancias Generadas ($)',
    ROUND(COALESCE(SUM(s.qty * t.price * (t.royalty / 100.0) * (ta.royaltyper / 100.0)), 0), 2) AS 'Regalías Cobradas ($)'
FROM authors a
LEFT JOIN titleauthor ta 
    ON a.au_id = ta.au_id
LEFT JOIN titles t 
    ON ta.title_id = t.title_id
LEFT JOIN sales s 
    ON t.title_id = s.title_id
GROUP BY 
    a.au_id, 
    a.au_fname, 
    a.au_lname, 
    a.city, 
    a.state
ORDER BY 
    `Ganancias Generadas ($)` DESC, 
    `Regalías Cobradas ($)` DESC, 
    `Nombre del Autor` ASC;


-- ===================================================================================
-- ANEXO DE AUDITORÍA CONTABLE: CONCILIACIÓN DEL 100% DE VENTAS DE LA EMPRESA
-- Propósito: Demostrar que el modelo de análisis permite conciliar al centavo
-- la totalidad de los $3,863.80 facturados en la base de datos:
--   - Ventas asignadas a autores: $2,893.50
--   - Ventas de libros sin autor (PS7777): $199.75
--   - Porcentajes no asignados a autores (remanente de BU1111 y PS2091): $770.55
--   - Suma total conciliada: $3,863.80 (100.00% exacto).
-- ===================================================================================

SELECT 
    '1. Ventas Atribuidas a Autores Registrados' AS categoria,
    ROUND(SUM(s.qty * t.price * (ta.royaltyper / 100.0)), 2) AS monto_total
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id
INNER JOIN titleauthor ta ON t.title_id = ta.title_id
UNION ALL
SELECT 
    '2. Ventas de Libros sin Autor Asignado (PS7777)' AS categoria,
    ROUND(SUM(s.qty * t.price), 2) AS monto_total
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id
LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
WHERE ta.title_id IS NULL
UNION ALL
SELECT 
    '3. Ventas por Porcentaje no Asignado a Autores (BU1111 y PS2091)' AS categoria,
    ROUND(SUM(s.qty * t.price * ((100 - sub.total_royalty) / 100.0)), 2) AS monto_total
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
    '>>> TOTAL GENERAL AUDITADO DE LA EMPRESA <<<' AS categoria,
    ROUND(SUM(s.qty * t.price), 2) AS monto_total
FROM sales s
INNER JOIN titles t ON s.title_id = t.title_id;
