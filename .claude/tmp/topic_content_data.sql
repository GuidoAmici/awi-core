-- Migration: populate topic_content from posts.js
-- Generated: 2026-03-03T09:28:19.674Z

TRUNCATE topic_content;

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  1,
  'Las cinco variables que sostienen una planta: ninguna es opcional',
  'Variables básicas',
  'Identificación simple',
  'Identificar las cinco variables que sostienen la vida de una planta y entender que la ausencia o exceso de cualquiera puede colapsar el sistema completo.',
  'Error frecuente',
  'Cuando algo falla, el primer instinto es agregar fertilizante. Esa decisión asume que el problema es siempre nutricional — y en la mayoría de los casos no lo es.',
  'Qué ocurre realmente',
  'Una planta no tiene una sola necesidad: tiene cinco simultáneas. Agua, luz, temperatura, humedad ambiental y nutrientes son las variables que mantienen activos los procesos metabólicos básicos. Cada una cumple una función específica e irreemplazable.

El agua transporta minerales disueltos desde la raíz hacia los tejidos. La luz es la fuente de energía para la fotosíntesis. La temperatura regula la velocidad de todas las reacciones enzimáticas. La humedad ambiental controla la velocidad de transpiración y el movimiento de agua dentro de la planta. Los nutrientes son la materia prima para construir tejidos y moléculas.

Ninguna de estas variables puede compensar la ausencia de otra.',
  'Cadena causa → efecto → síntoma observable',
  '["Temperatura > 30°C → estomas cerrados para evitar pérdida hídrica → fotosíntesis detenida aunque haya luz suficiente → hojas enrolladas hacia arriba","HR < 35% → transpiración excesiva → pérdida de turgencia → puntas y bordes secos aunque el sustrato esté húmedo","Sustrato sin drenaje → raíces sin oxígeno → muerte radicular progresiva → síntomas idénticos a deficiencia severa"]'::jsonb,
  'Hipótesis a descartar',
  'Si una planta muestra síntomas de deficiencia y el primer movimiento es agregar fertilizante sin verificar pH, temperatura, humedad y estado radicular, el diagnóstico está incompleto. Los nutrientes existen en el sustrato pero no están disponibles si alguna otra variable los bloquea.',
  'El diagnóstico correcto empieza por identificar cuál de las cinco variables está fallando. No por asumir que siempre es la misma.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  2,
  'Variable dominante: por qué solo una variable manda en cada momento',
  'Prioridad',
  'Priorización',
  'Entender que en cualquier momento existe una sola variable que limita el rendimiento del cultivo más que todas las demás, y que identificarla es la habilidad técnica más valiosa.',
  'Error frecuente',
  'Frente a un problema, la mayoría ajusta pH, riega, cambia la luz y agrega nutrientes el mismo día. Si algo mejora, no saben qué lo arregló. Si algo empeora, no saben qué lo causó.',
  'Qué ocurre realmente',
  'En cualquier sistema productivo, existe un factor que limita el rendimiento global más que cualquier otro. Mejorar cualquier otra variable sin resolver la limitante no produce cambios observables.

En cultivo indoor, si la temperatura del canopy es de 34°C, los estomas están cerrados y la fotosíntesis está detenida. En ese contexto, ajustar el pH o cambiar la solución nutritiva no produce ninguna mejora visible. La temperatura es la variable dominante del momento — y seguirá siéndolo hasta que se corrija.',
  'Cadena causa → efecto → síntoma observable',
  '["pH < 5.5 → mecanismos de transporte iónico fallan → nutrientes no atraviesan membrana celular → clorosis aunque el fertilizante sea correcto","Sin diagnóstico: aumentar dosis → mayor EC → estrés osmótico → raíces quemadas y síntomas que se agravan","Corregir solo el pH → transportadores iónicos vuelven a operar → recuperación visible en 48–72 horas sin cambiar nada más"]'::jsonb,
  'Hipótesis a descartar',
  'Que varios problemas simultáneos requieren varias correcciones simultáneas. Los síntomas que parecen múltiples casi siempre tienen una causa raíz única. Intervenir en paralelo impide saber qué variable limitaba el sistema.',
  'Un cambio por vez. Observá 48–72 horas. Si el síntoma mejora, identificaste la variable dominante.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  3,
  'Por qué cada intervención sin diagnóstico destruye información',
  'Intervención',
  'Causa–efecto simple',
  'Comprender que cada modificación realizada sin diagnóstico previo elimina la posibilidad de entender qué estaba fallando, generando una cadena de errores difícil de revertir.',
  'Error frecuente',
  'Ver un síntoma y actuar de inmediato. Intervenir sin diagnóstico no es resolver el problema — es generar uno nuevo encima del original.',
  'Qué ocurre realmente',
  'Cada variable del cultivo está en relación con las demás. Cuando se modifica una sin entender el estado del sistema, se introducen cambios que afectan otras variables de forma impredecible.

El sustrato tiene un equilibrio de sales, pH y estructura porosa. El ambiente tiene un equilibrio de temperatura, humedad y CO₂. Modificar una variable cambia ese equilibrio — y si la causa raíz no se identificó, el nuevo estado puede ser peor que el original.',
  'Cadena causa → efecto → síntoma observable',
  '["Temperatura alta bloquea absorción → hojas amarillas","Sin diagnóstico: se agrega fertilizante → EC sube → estrés osmótico → más síntomas","Sin diagnóstico: se baja pH para ''mejorar absorción'' → pH bajo con CE alta quema raíces → colapso","Causa raíz nunca resuelta: temperatura. Todas las intervenciones empeoraron sin atacar el origen."]'::jsonb,
  'Hipótesis a descartar',
  'Que actuar rápido es mejor que observar primero. Las plantas tienen ciclos metabólicos que responden en horas o días. Esperar 24 horas para observar la evolución de un síntoma antes de intervenir casi siempre produce mejores resultados.',
  'El diagnóstico no es tiempo perdido. Es la única forma de saber qué variable estás corrigiendo y si la corrección funcionó.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  4,
  'Cómo funciona el riego: el ciclo húmedo–seco no es opcional',
  'Agua',
  'Observación',
  'Entender que el riego correcto no sigue un calendario sino el estado real del sustrato, y que el ciclo entre saturación y secado es el mecanismo que permite la absorción activa de nutrientes.',
  'Error frecuente',
  'Regar cada dos días porque ''toca''. Este patrón ignora temperatura, tamaño de la planta, tipo de sustrato y estadio de crecimiento — todos factores que determinan cuándo el sustrato necesita agua.',
  'Qué ocurre realmente',
  'Las raíces necesitan dos cosas que no pueden tener al mismo tiempo: agua y oxígeno. Cuando el sustrato está saturado, los poros capilares están llenos de agua y el oxígeno ha sido desplazado.

A medida que el sustrato se seca, el agua drena y el oxígeno vuelve a ocupar los poros superiores. En ese intervalo las raíces respiran activamente, generan ATP mediante respiración celular y usan esa energía para absorber minerales de forma activa contra el gradiente de concentración.

Ese ciclo húmedo–seco es el mecanismo real de absorción. Sin él, la nutrición falla aunque la solución nutritiva sea perfecta.',
  'Cadena causa → efecto → síntoma observable',
  '["Sustrato siempre húmedo → raíces sin oxígeno → respiración inhibida → absorción detenida → síntomas de deficiencia con fertilizante presente","Ciclo húmedo–seco respetado → raíces alternan hidratación y oxigenación → absorción activa funcional → crecimiento sostenido"]'::jsonb,
  'Hipótesis a descartar',
  'Que el sustrato debe mantenerse siempre húmedo para que la planta tenga agua disponible. La planta no absorbe agua pasivamente cuando el sustrato está saturado — la absorbe activamente cuando las raíces tienen energía para hacerlo, y esa energía requiere oxígeno.',
  'El peso de la maceta es el instrumento más preciso para decidir cuándo regar. Si pesa poco, las raíces están en su punto óptimo de absorción.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  5,
  'Exceso de riego: el síntoma que se parece a todo lo demás',
  'Agua',
  'Diagnóstico visual',
  'Reconocer los síntomas visuales específicos del sobre-riego y distinguirlos de otras causas con síntomas superficialmente similares.',
  'Error frecuente',
  'Ver hojas caídas y regar más. El sobre-riego produce síntomas que se parecen exactamente a la falta de agua, lo que lleva a los cultivadores a agravar el problema con más riego.',
  'Qué ocurre realmente',
  'Cuando el sustrato está permanentemente húmedo, las raíces no pueden respirar. Sin oxígeno, la respiración celular se detiene y las raíces no generan el ATP necesario para las bombas iónicas que mueven el agua hacia el interior de la célula.

El resultado es paradójico: las células de la raíz no pueden absorber agua aunque estén rodeadas de ella. La presión de turgencia en las células foliares cae y las hojas pierden rigidez — exactamente igual que cuando hay falta de agua. La diferencia está en el sustrato: húmedo en sobre-riego, seco en déficit hídrico.',
  'Cadena causa → efecto → síntoma observable',
  '["Sustrato saturado → desplazamiento de O₂ radicular → inhibición de respiración celular → ATP insuficiente para bombas de absorción → turgencia foliar cae → hojas caídas y blandas con sustrato mojado","Diagnóstico erróneo: más riego → mayor saturación → mayor inhibición radicular → posible pudrición radicular → colapso progresivo"]'::jsonb,
  'Hipótesis a descartar',
  'Que hojas caídas siempre indica falta de agua. El síntoma visual es idéntico pero la causa es opuesta. La forma de distinguirlos es directa: levantá la maceta. Si pesa, el sustrato tiene agua suficiente y las raíces no pueden usarla.',
  'Antes de regar, verificá el peso de la maceta. El sustrato húmedo con planta caída es sobre-riego hasta que se demuestre lo contrario.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  6,
  'Déficit hídrico real: cuándo la planta sí necesita agua',
  'Agua',
  'Comparación',
  'Identificar los síntomas específicos del déficit hídrico real y distinguirlos de condiciones que producen síntomas visualmente similares pero con causas diferentes.',
  'Error frecuente',
  'Interpretar cualquier marchitamiento como déficit hídrico y agregar agua sin verificar el estado del sustrato. En muchos casos se riega sobre un sustrato que ya tiene agua suficiente, agravando el problema real.',
  'Qué ocurre realmente',
  'El déficit hídrico real ocurre cuando el contenido de agua en el sustrato cae por debajo del punto en que las raíces pueden absorber suficiente para mantener la turgencia foliar. Las células pierden agua, las vacuolas se contraen y los tejidos foliares se ablandan.

Este proceso es reversible si se actúa a tiempo: en déficit hídrico simple, la planta recupera turgencia dentro de 2–4 horas después del riego. Esa velocidad de recuperación es el indicador diagnóstico más confiable.',
  'Cadena causa → efecto → síntoma observable',
  '["Sustrato seco → gradiente osmótico insuficiente → células foliares pierden turgencia → hojas blandas y doblegadas, tallos sin rigidez","Riego adecuado → osmosis pasiva restablecida → turgencia recuperada en 2–4 horas → hojas firmes","Sin recuperación en 4 hs post-riego → el problema no era falta de agua → revisar temperatura, estado radicular y pH"]'::jsonb,
  'Hipótesis a descartar',
  'Que el marchitamiento con sustrato seco siempre indica déficit hídrico simple. En ambientes con HR < 35%, la planta puede mostrar síntomas de marchitamiento aunque el sustrato esté en su punto correcto de secado — la variable dominante es la humedad ambiental, no el agua en el sustrato.',
  'El marcador diagnóstico del déficit hídrico real es la recuperación rápida post-riego. Sin esa confirmación, el diagnóstico está incompleto.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  7,
  'La luz no es decoración: es la única fuente de energía del sistema',
  'Luz',
  'Conceptual básico',
  'Comprender que la luz es el insumo energético primario del cultivo y que más intensidad no equivale a más productividad cuando se supera el umbral de saturación fotosintética.',
  'Error frecuente',
  'Acercar la lámpara para acelerar el crecimiento. Esta decisión ignora que la fotosíntesis tiene un límite físico: por encima de cierta intensidad la planta no puede usar más luz y los excedentes generan calor y estrés oxidativo.',
  'Qué ocurre realmente',
  'La fotosíntesis convierte energía lumínica en energía química (ATP y NADPH) dentro de los cloroplastos. Este proceso tiene una velocidad máxima determinada por la cantidad de clorofila disponible y la temperatura del tejido foliar.

Cuando la intensidad supera el punto de saturación fotosintética, el exceso de fotones activa vías de fotoprotección: las células producen antocianinas y carotenoides para disipar energía como calor. Las hojas se tornan amarillentas en las zonas más expuestas — no porque les falte algo, sino porque están activando defensas contra el exceso de energía.

El PPFD (densidad de flujo de fotones fotosintéticos) mide cuánta luz utilizable llega a cada punto del canopy.',
  'Cadena causa → efecto → síntoma observable',
  '["PPFD > 900 μmol/m²/s en vegetativo → saturación de centros de reacción → activación de fotoprotección → hojas superiores amarillas o con bordes marrones → crecimiento detenido pese a alta intensidad","PPFD en rango (400–600 veg / 600–900 flor) → fotosíntesis activa sin estrés → verde uniforme y elongación internodal normal"]'::jsonb,
  'Hipótesis a descartar',
  'Que el amarillamiento en hojas superiores bajo luz intensa indica deficiencia de nitrógeno. El patrón espacial es el indicador: si ocurre en las hojas más cercanas a la lámpara y no en las inferiores, la causa es fotoinhibición por exceso de luz, no deficiencia nutricional.',
  'La distancia entre la lámpara y el canopy no es un ajuste estético. Es la variable que define si la intensidad está dentro del rango productivo de la planta.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  8,
  'Temperatura: el regulador de velocidad de todo lo que ocurre',
  'Temperatura',
  'Rango seguro',
  'Entender los rangos de temperatura funcionales por fase y por qué los extremos no solo frenan el crecimiento sino que activan respuestas de estrés que confunden el diagnóstico.',
  'Error frecuente',
  'Medir la temperatura del cuarto en lugar de la temperatura a nivel del canopy. La diferencia puede ser de 6–10°C, especialmente con lámparas de alta potencia o poca circulación de aire.',
  'Qué ocurre realmente',
  'La temperatura regula la velocidad de las reacciones enzimáticas. Cada enzima implicada en fotosíntesis, respiración y transporte de nutrientes tiene un rango óptimo y se desnaturaliza fuera de él.

Por encima de 30°C a nivel foliar, la enzima RuBisCO pierde eficiencia y comienza a catalizar una reacción alternativa que consume energía sin producir azúcares (fotorrespiración). Los estomas se cierran para reducir pérdida hídrica, lo que también cierra la entrada de CO₂.

Por debajo de 15°C, las reacciones metabólicas se vuelven tan lentas que el crecimiento cesa y la humedad relativa del aire frío aumenta el riesgo de hongos.',
  'Cadena causa → efecto → síntoma observable',
  '["Temperatura canopy > 30°C → estomas cerrados → CO₂ bloqueado → fotosíntesis detenida → hojas enrolladas hacia arriba","Temperatura < 15°C → velocidad enzimática mínima → crecimiento detenido → coloración púrpura por acumulación de antocianinas","Temperatura 22–26°C canopy → enzimas en rango óptimo → fotosíntesis activa → crecimiento sostenido y hojas planas"]'::jsonb,
  'Hipótesis a descartar',
  'Que la temperatura del cuarto es suficiente para diagnosticar problemas térmicos. El tejido foliar puede estar varios grados por encima de la temperatura ambiente si la circulación de aire es insuficiente o si la lámpara irradia calor directamente sobre el canopy.',
  'La temperatura que importa es la del canopy. Todo lo demás es una aproximación.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  9,
  'Humedad ambiental: por qué el aire también puede secar una planta',
  'Humedad',
  'Relación simple',
  'Entender que la humedad relativa del ambiente es una variable independiente del riego, y que un déficit de vapor en el aire puede producir estrés hídrico foliar aunque el sustrato esté correctamente hidratado.',
  'Error frecuente',
  'Responder al marchitamiento foliar en ambientes secos aumentando el riego. El problema no está en el sustrato — está en que la planta transpira más agua por las hojas de la que puede absorber por las raíces.',
  'Qué ocurre realmente',
  'La transpiración foliar es el motor del flujo de agua dentro de la planta. El agua se evapora por los estomas cuando la presión de vapor dentro de la hoja es mayor que la presión de vapor del aire circundante. Cuanto más seco el aire (menor HR), mayor la diferencia de presión y mayor la velocidad de transpiración.

Cuando la HR cae por debajo del 35–40%, la demanda evaporativa del ambiente supera la capacidad de absorción radicular. Las células foliares pierden agua más rápido de lo que se repone — aunque el sustrato esté en condiciones correctas.',
  'Cadena causa → efecto → síntoma observable',
  '["HR < 35% → alto gradiente de presión de vapor → transpiración excesiva → pérdida de turgencia foliar → hojas blandas y bordes secos con sustrato en condición normal","Más riego en ese contexto → mayor EC en sustrato → estrés osmótico → problema original no resuelto más problema nuevo","Corrección de HR a 50–60% → gradiente equilibrado → transpiración normalizada → turgencia recuperada sin cambiar el riego"]'::jsonb,
  'Hipótesis a descartar',
  'Que el marchitamiento con sustrato húmedo siempre indica sobre-riego. En ambientes con baja HR, la planta puede mostrar el mismo síntoma con el sustrato en condiciones correctas. La diferencia se establece midiendo la HR: si está por debajo del 40% y el sustrato no está saturado, la variable dominante es la humedad ambiental.',
  'Un termómetro/higrómetro a la altura del canopy es el instrumento más útil del cuarto. Temperatura y humedad se miden juntas porque su efecto es siempre combinado.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  10,
  'Cómo descartar hipótesis: el método que convierte síntomas en diagnósticos',
  'Priorización',
  'Descarte lógico',
  'Aplicar un proceso de eliminación sistemática para identificar la variable dominante cuando múltiples síntomas apuntan a múltiples causas posibles.',
  'Error frecuente',
  'Actuar sobre la primera hipótesis que surge sin contrastarla con la evidencia disponible. La mayoría de los síntomas en cultivo indoor son compatibles con al menos tres causas distintas — sin proceso de descarte, el diagnóstico es una apuesta.',
  'Qué ocurre realmente',
  'El diagnóstico técnico no parte de lo que parece más probable: parte de lo que puede medirse primero. Las cinco variables tienen distinta facilidad de medición. Temperatura y humedad se miden en segundos. El pH y EC del agua de entrada se miden en minutos. El estado del sustrato se evalúa por peso y textura. El estado radicular requiere observación directa.

El proceso de descarte sigue ese orden: primero lo más rápido, luego lo más costoso en tiempo. Cada variable descartada reduce el espacio de diagnóstico hasta que solo queda una hipótesis activa.',
  'Cadena causa → efecto → síntoma observable',
  '["Hojas amarillas → hipótesis: deficiencia de N → verificar patrón: ¿hojas viejas o nuevas? → si son viejas, N es móvil → posible déficit","Antes de agregar N: medir pH → pH 7.5 → absorción de N bloqueada → la causa es el pH, no la cantidad de N","Corrección del pH → absorción normalizada → amarillamiento se detiene en 48–72 hs → hipótesis nutricional descartada"]'::jsonb,
  'Hipótesis a descartar',
  'Que el síntoma visual identifica la causa. El amarillamiento puede indicar deficiencia de nitrógeno, pH incorrecto, sobre-riego, temperatura extrema o exceso de luz. Ningún síntoma aislado permite un diagnóstico definitivo.',
  'El descarte es una habilidad técnica, no un temperamento. Se aprende practicando el mismo proceso en cada problema: medir, contrastar, eliminar, confirmar.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  11,
  'pH: no es acidez del agua, es la llave que abre o cierra la nutrición',
  'pH + absorción',
  'Comprensión técnica',
  'Comprender que el pH no mide acidez del agua sino que determina qué nutrientes pueden atravesar la membrana radicular y cuáles quedan bloqueados aunque estén presentes.',
  'Error frecuente',
  'Ajustar el pH hasta un número específico memorizando ''lo que dice el manual'' sin entender qué mecanismo biológico ese número está controlando.',
  'Qué ocurre realmente',
  'Los nutrientes minerales existen en solución en distintas formas iónicas según el pH. El hierro, por ejemplo, existe principalmente como Fe³⁺ a pH alcalino — una forma que las proteínas transportadoras de la membrana radicular no pueden capturar. A pH 6.0–6.5, el hierro forma Fe²⁺, la forma que los transportadores reconocen.

Cada nutriente tiene un rango de pH en el que su forma iónica es compatible con los transportadores de membrana. A pH 7.5, el hierro, el manganeso y el zinc quedan inaccesibles. A pH 4.5, el calcio y el magnesio precipitan como sales insolubles.

Por eso el pH no es una preferencia: es el parámetro que define qué nutrientes están disponibles para absorción.',
  'Cadena causa → efecto → síntoma observable',
  '["pH 7.5 → Fe³⁺ no reconocido por transportadores → absorción de hierro bloqueada → clorosis intervenal en hojas nuevas","Aplicar quelato de hierro sin corregir pH → mejora temporal → reaparece al acabarse el quelato → ciclo repetido sin solución estructural","Corrección de pH a 6.0–6.5 → Fe²⁺ disponible → absorción normalizada → clorosis desaparece en 5–7 días"]'::jsonb,
  'Hipótesis a descartar',
  'Que la clorosis intervenal en hojas nuevas siempre indica falta de hierro en solución. El hierro puede estar en concentración correcta y ser completamente inaccesible si el pH está fuera del rango de disponibilidad. Añadir más quelatos de hierro sobre un pH de 7.5 es un tratamiento sintomático que no resuelve la causa.',
  'El pH no es un número a memorizar: es el parámetro que controla la biodisponibilidad de cada elemento. Entender qué nutriente se bloquea a qué rango convierte el ajuste de pH en diagnóstico, no en rutina.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  12,
  'EC: lo que la conductividad mide no es fertilizante sino presión osmótica',
  'EC + concentración de sales',
  'Relación sales–nutrientes',
  'Entender que la conductividad eléctrica no mide cantidad de nutrientes sino concentración total de sales, y que una EC alta puede bloquear la absorción de agua aunque los nutrientes estén perfectamente balanceados.',
  'Error frecuente',
  'Interpretar una EC baja como señal de que ''faltan nutrientes'' y agregar más fertilizante hasta alcanzar el número deseado, sin evaluar primero si la EC baja proviene de dilución o de un sustrato lavado.',
  'Qué ocurre realmente',
  'La EC mide la capacidad del agua de conducir electricidad, que depende de la cantidad de iones disueltos. Más sales disueltas — independientemente de cuáles sean — producen mayor EC.

El problema central es osmótico. La absorción de agua por las raíces ocurre por ósmosis: el agua se mueve desde la zona de menor concentración de solutos (solución del sustrato) hacia el interior de la célula radicular. Cuando la EC del sustrato es alta, la concentración de solutos afuera puede superar la concentración interna — el gradiente osmótico se invierte y el agua sale de la célula. Esto se llama plasmólisis.',
  'Cadena causa → efecto → síntoma observable',
  '["EC > 3.5 mS/cm → gradiente osmótico invertido → pérdida de agua celular en raíces → plasmólisis → absorción de agua y nutrientes detenida → síntomas de déficit hídrico y nutricional simultáneos","Adición de más fertilizante sobre EC alta → EC aumenta → gradiente osmótico empeora → síntomas se agravan → toxicidad por sales","Lavado del sustrato con agua de baja EC → sales arrastradas → gradiente osmótico normalizado → absorción restablecida en 24–48 horas"]'::jsonb,
  'Hipótesis a descartar',
  'Que una EC alta indica nutrición abundante. Una EC alta indica alta concentración de sales — que pueden ser los nutrientes correctos, sales residuales de riegos anteriores, o carbonatos del agua de red. Sin analizar el tipo de sales presentes, ajustar EC por número es un movimiento ciego.',
  'EC y pH son las dos variables que determinan si los nutrientes en el sustrato son accesibles. Medirlas juntas no es una recomendación: es el mínimo para hacer un diagnóstico nutricional válido.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  13,
  'Riego y oxigenación radicular: la relación que nadie ve hasta que es tarde',
  'Agua + raíces',
  'Relación sistémica',
  'Comprender que el riego no solo hidrata sino que determina el acceso de las raíces al oxígeno, y que la ausencia de oxígeno en la zona radicular colapsa funciones que no parecen relacionadas con el agua.',
  'Error frecuente',
  'Evaluar el riego solo por la superficie del sustrato. La zona radicular activa está entre 5 y 15 cm de profundidad, y puede estar saturada aunque la superficie parezca seca.',
  'Qué ocurre realmente',
  'Las raíces son tejido vivo que consume oxígeno para mantener sus funciones. La respiración aeróbica radicular produce el ATP que alimenta las bombas iónicas responsables de absorber minerales contra el gradiente de concentración. Sin oxígeno, esas bombas se apagan.

El oxígeno llega a las raíces a través de los macro-poros del sustrato — los espacios entre partículas que no se llenan con agua capilar. Cuando el sustrato está saturado, esos poros están ocupados por agua. En sustratos compactos o con poca perlita, el drenaje es lento y la saturación persiste por más tiempo.',
  'Cadena causa → efecto → síntoma observable',
  '["Sustrato compacto + riego frecuente → macro-poros siempre saturados → raíces sin O₂ por períodos prolongados → ATP insuficiente → bombas iónicas apagadas → deficiencias de Ca y Mg visibles aunque ambos estén en solución","Mejora de estructura (mayor perlita) + menor frecuencia de riego → ciclo húmedo–seco restablecido → oxigenación radicular recuperada → absorción de Ca y Mg normalizada sin cambiar la solución nutritiva"]'::jsonb,
  'Hipótesis a descartar',
  'Que las deficiencias de calcio y magnesio se resuelven siempre agregando calcio y magnesio. Estos elementos son relativamente inmovilizables y su absorción depende de bombas activas que requieren ATP. Si las raíces están sin oxígeno, ninguna cantidad de Ca-Mg en solución va a ser absorbida.',
  'El oxígeno en la zona radicular no es visible ni medible sin instrumentos, pero sus efectos son completamente predecibles. La estructura del sustrato y la frecuencia de riego son las dos variables que lo controlan.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  14,
  'Temperatura, humedad y absorción: las tres variables que se mueven juntas',
  'Temperatura + humedad + absorción',
  'Pensamiento sistémico básico',
  'Comprender que temperatura y humedad no afectan la planta de forma independiente sino a través de una variable combinada (el VPD) que determina la velocidad de transpiración y el ritmo de absorción de nutrientes.',
  'Error frecuente',
  'Corregir temperatura y humedad por separado sin considerar su relación, llegando a combinaciones que mantienen el estrés aunque cada parámetro individual esté en rango.',
  'Qué ocurre realmente',
  'El VPD (déficit de presión de vapor) es la diferencia entre la presión de vapor que el aire podría contener a una temperatura dada y la que realmente contiene. Es la medida real de cuánta capacidad tiene el aire para absorber vapor de agua desde las hojas.

Un VPD alto (aire cálido y seco) acelera la transpiración y el flujo de xilema — los nutrientes son arrastrados hacia arriba con el agua. Un VPD bajo (aire frío y húmedo) frena la transpiración y detiene el flujo de xilema — la absorción de calcio, que depende casi exclusivamente de ese flujo, colapsa.

Temperatura 28°C con HR 40% produce VPD ~2.2 kPa — estrés por transpiración excesiva. Temperatura 20°C con HR 75% produce VPD ~0.6 kPa — absorción de calcio detenida. Ambas son problemáticas aunque cada variable individual parezca aceptable.',
  'Cadena causa → efecto → síntoma observable',
  '["VPD < 0.8 kPa (frío y húmedo) → transpiración mínima → flujo de xilema detenido → calcio no se mueve hasta tejidos nuevos → puntas quemadas en hojas jóvenes (tip burn) aunque el calcio en solución sea correcto","VPD > 1.6 kPa (cálido y seco) → transpiración excesiva → demanda hídrica supera absorción → estrés hídrico foliar → estomas cerrados → fotosíntesis detenida","VPD en rango 0.8–1.2 kPa → equilibrio entre transpiración y absorción → calcio móvil → crecimiento sin tip burn"]'::jsonb,
  'Hipótesis a descartar',
  'Que el tip burn en hojas jóvenes es siempre deficiencia de calcio soluble. Si el VPD es bajo, el calcio puede estar en solución en concentración correcta y aun así no llegar a las hojas jóvenes porque el flujo de xilema está detenido. Agregar más calcio sin corregir el VPD no resuelve el tip burn.',
  'Temperatura y humedad son dos parámetros, pero su efecto sobre la planta es uno solo: el VPD. Optimizarlos por separado sin calcular su resultado combinado es operar con información incompleta.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  15,
  'Síntoma vs causa real: por qué tratar el síntoma prolonga el problema',
  'Síntoma + variable causal',
  'Diagnóstico estructurado',
  'Establecer un proceso de diagnóstico que parte del síntoma visible y llega a la variable causal real mediante eliminación, sin asumir que el síntoma y la causa comparten nombre.',
  'Error frecuente',
  'Nombrar el síntoma como si fuera el diagnóstico. ''Deficiencia de hierro'' describe lo que se ve, no por qué está ocurriendo. Tratar el síntoma sin identificar la causa produce mejoras transitorias que vuelven a aparecer.',
  'Qué ocurre realmente',
  'Los síntomas en cultivo indoor no son específicos de una sola causa. La clorosis intervenal puede indicar deficiencia de hierro, de magnesio, de manganeso, pH bloqueante, sobre-riego que inhibió absorción, o temperatura extrema. El mismo aspecto visual tiene al menos seis causas posibles.

El diagnóstico estructurado parte de una premisa: el síntoma es el punto de entrada, no el destino. El camino entre ambos se recorre midiendo las variables accesibles en orden de facilidad y descartando hipótesis hasta que solo queda una.

La distribución del síntoma en la planta es el primer filtro: síntomas en hojas viejas → deficiencias de elementos móviles (N, P, K, Mg). Síntomas en hojas nuevas → deficiencias de elementos inmóviles (Ca, Fe, Mn, Zn). Esta diferencia elimina la mitad de las hipótesis antes de medir nada.',
  'Cadena causa → efecto → síntoma observable',
  '["Clorosis intervenal en hojas nuevas → elemento inmóvil afectado → candidatos: Fe, Mn, Zn, Ca","Medición de pH: 7.2 → rango en que Fe, Mn y Zn quedan bloqueados → hipótesis principal: pH bloqueante","Corrección de pH a 6.0 → síntoma se detiene en 48–72 hs → causa confirmada: pH, no deficiencia de microelementos","Si no mejora tras corrección de pH → evaluar VPD (posible bloqueo de Ca por transpiración baja) → siguiente hipótesis activa"]'::jsonb,
  'Hipótesis a descartar',
  'Que el nombre del síntoma es suficiente para determinar el tratamiento. ''Deficiencia de hierro'' como diagnóstico lleva a agregar hierro. Pero si la causa real es pH 7.2, el hierro agregado tampoco será absorbido, la EC del sustrato sube y el estado de la planta empeora.',
  'El diagnóstico estructurado no es un método lento — es el método que evita repetir el mismo error en el siguiente cultivo. Cada causa identificada correctamente es una hipótesis que ya no necesitás probar de nuevo.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  16,
  'Medir no es opcional: por qué el dato cambia la decisión antes de que actúes',
  'Medición vs intuición',
  'Decisión basada en datos',
  'Comprender que la medición no confirma lo que ya creés saber — genera información nueva que actualiza el diagnóstico de forma objetiva, independientemente de la experiencia previa del cultivador.',
  'Error frecuente',
  'Medir después de haber decidido, para confirmar que la decisión es correcta. En ese caso el instrumento no está informando la decisión: está siendo usado para justificarla. La medición confirmatoria es un sesgo disfrazado de técnica.',
  'Qué ocurre realmente',
  'La intuición es un modelo mental construido a partir de experiencias pasadas. En condiciones estables y conocidas, puede ser útil. Pero en cultivo indoor, las variables cambian de forma continua: el agua de red varía estacionalmente, el pH del sustrato deriva con riegos sucesivos, la EC sube cuando el agua se evapora sin que se evaporen las sales.

Cuando se toma una decisión sin medir, el modelo mental está basado en el estado anterior del sistema, no en el estado actual. La medición no confirma el modelo — lo actualiza.

La diferencia operativa es concreta: el cultivador que mide antes de actuar tiene información del momento presente. El cultivador que actúa sin medir aplica la solución del problema anterior al problema de hoy. Son problemas similares, pero raramente idénticos.',
  'Cadena causa → efecto → diferencia operativa',
  '["Sin medición: síntomas de deficiencia → intuición: ''le falta nitrógeno'' → agrega N → EC sube → estrés osmótico → síntomas empeoran → segunda hipótesis incorrecta construida sobre la primera","Con medición previa: síntomas → mide pH: 7.1 → diagnóstica bloqueo de absorción por pH alto → corrige solo el pH → síntomas mejoran en 48 hs sin agregar nutrientes","Diferencia clave: la medición produjo un diagnóstico distinto al que la intuición hubiera generado — la misma experiencia de base, distinto resultado"]'::jsonb,
  'Hipótesis a descartar',
  'Que medir es útil solo cuando hay problemas visibles. El valor de la medición preventiva es que detecta desvíos antes de que produzcan síntomas. Un pH que subió de 6.2 a 7.0 en tres días no produce síntomas inmediatos — los producirá en cinco días. El instrumento lo detecta mientras aún hay margen de corrección simple.',
  'La experiencia sin datos genera confianza en el modelo propio. Los datos sin experiencia generan números sin interpretación. La combinación de ambos es lo que produce decisiones técnicamente sólidas: el criterio del cultivador informa qué medir, el instrumento informa sobre qué decidir.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  17,
  'Cómo medir pH sin que el procedimiento invalide el resultado',
  'Procedimiento de medición de pH',
  'Método técnico',
  'Ejecutar el procedimiento correcto de medición de pH, identificando los errores operativos que generan lecturas falsas independientemente de la precisión del instrumento.',
  'Error frecuente',
  'Medir directamente en el sustrato húmedo o en el agua del reservorio sin agitar. Estas prácticas producen lecturas que no representan el pH real de la solución que las raíces están absorbiendo.',
  'Qué ocurre realmente',
  'El pHmetro tiene una membrana de vidrio que genera un potencial eléctrico proporcional a la concentración de iones H⁺ en el líquido en contacto. Para que esa lectura sea válida, se necesitan tres condiciones simultáneas.

Primero, la solución debe ser homogénea. El agua no mezclada se estratifica: la zona superficial, más oxigenada, puede tener un pH diferente al de la zona profunda. Medir sin agitar es medir una capa, no la solución.

Segundo, la sonda debe estar limpia y calibrada. Las sales que precipitan sobre la membrana de vidrio alteran el potencial medido. Un electrodo con depósitos de KCl seco puede leer hasta 0.3–0.5 unidades fuera del valor real.

Tercero, la temperatura importa. La disociación de iones H⁺ cambia con la temperatura. Los pHmetros sin compensación de temperatura asumen 25°C como referencia — una solución a 15°C o 35°C dará una lectura sistemáticamente desviada si no se aplica corrección.',
  'Cadena causa → efecto → error de diagnóstico',
  '["Reservorio no agitado con pH real 5.8 → zona superficial oxigenada con pH 6.2 → medición superficial: 6.2 → decisión: ''pH correcto'' → zona profunda y raíces en contacto con pH 5.4 → absorción de elementos alterada","Sonda con membrana sucia → lectura 0.4 unidades alta → pH real 5.6 medido como 6.0 → decisión: ''ok'' → bloqueo de hierro y manganeso durante semanas sin diagnóstico","Procedimiento correcto: agitar 30 seg → esperar estabilización → medir en zona media → leer cuando el display deja de cambiar (estabilización)"]'::jsonb,
  'Hipótesis a descartar',
  'Que el pH del agua del grifo medido antes de mezclar el fertilizante es el pH que las raíces reciben. La mezcla del fertilizante, la interacción con el sustrato y la actividad radicular cambian el pH de forma significativa. La medición válida es la de la solución final homogeneizada, después de mezclar todo, tomada en el punto de aplicación o del runoff.',
  'Un pHmetro de calidad con procedimiento incorrecto produce datos incorrectos con alta confianza. El procedimiento no es un trámite — es la condición que hace que la lectura signifique algo.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  18,
  'Cómo medir EC sin que la temperatura o el equipo distorsionen el resultado',
  'Procedimiento de medición de EC',
  'Método técnico',
  'Ejecutar el procedimiento correcto de medición de conductividad eléctrica, controlando los factores externos que afectan la lectura y comprendiendo qué punto del sistema es el más informativo para medir.',
  'Error frecuente',
  'Medir EC insertando la sonda directamente en el sustrato y confiar en esa lectura como representativa de la solución que las raíces absorben. El sustrato compacto, la distribución heterogénea de sales y la variabilidad de temperatura producen lecturas con alta dispersión.',
  'Qué ocurre realmente',
  'El conductímetro mide la capacidad de una solución de conducir electricidad, que depende de la cantidad y tipo de iones disueltos. Dos factores externos afectan la lectura de forma sistemática y predecible.

Primero, la temperatura. La conductividad de cualquier solución aumenta aproximadamente un 2% por cada grado Celsius. Un conductímetro sin compensación de temperatura automática (ATC) reportará valores distintos para la misma solución a 20°C y a 30°C. En verano, sin compensación, una solución con EC real de 2.0 mS/cm puede medirse como 2.4 mS/cm.

Segundo, el estado de los electrodos. Las sales disueltas se depositan sobre las células de los electrodos con el uso. Estos depósitos alteran la geometría efectiva de la celda de medición y producen lecturas que se alejan del valor real de forma gradual.

El punto de muestreo también importa. La EC del agua de entrada al reservorio, la EC del runoff y la EC en el sustrato son tres valores distintos. El runoff es el más informativo porque refleja la acumulación de sales en la zona radicular.',
  'Cadena causa → efecto → error de gestión',
  '["Temperatura del agua: 32°C (verano, sin ATC) → conductímetro sin compensación → EC real 1.8 mS/cm medida como 2.2 mS/cm → decisión: ''EC alta, diluir'' → agua de riego muy diluida → planta recibe 1.4 mS/cm → nutrición insuficiente durante semanas","Electrodos con depósitos → lectura baja sistemáticamente → EC real 2.4 medida como 1.9 → decisión: ''EC baja, agregar fertilizante'' → EC real sube a 3.0 → estrés osmótico","Procedimiento correcto: enjuagar electrodos con agua destilada → agitar solución → esperar temperatura estable o usar ATC → medir en runoff post-riego"]'::jsonb,
  'Hipótesis a descartar',
  'Que la EC del reservorio recién mezclado es la EC que la raíz recibe. Cada ciclo de riego evapora agua y concentra sales en el sustrato. Si no se realizan lavados periódicos, la EC de la zona radicular puede ser significativamente más alta que la EC del agua de entrada, aunque el reservorio esté correctamente preparado.',
  'EC y temperatura son inseparables en la medición. Usá siempre conductímetros con ATC o tomá las mediciones a temperatura estable. Sin esa condición, comparás valores que no son comparables entre sí.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  19,
  'Calibración: por qué un instrumento sin calibrar produce certeza falsa',
  'Calibración + confiabilidad del dato',
  'Confiabilidad del dato',
  'Comprender que la calibración no es un procedimiento de inicio único sino una práctica continua, y que un instrumento descalibrado genera confianza en datos incorrectos — lo que es técnicamente peor que no tener datos.',
  'Error frecuente',
  'Calibrar el instrumento cuando se lo recibe y no volver a calibrarlo. Los pHmetros y conductímetros derivan gradualmente de su punto de referencia con el uso, la exposición a soluciones concentradas y las variaciones de temperatura. La deriva es lenta e invisible hasta que produce un error relevante.',
  'Qué ocurre realmente',
  'El pHmetro funciona con una membrana de vidrio que genera un potencial eléctrico proporcional a la concentración de H⁺. Esta membrana envejece: acumula iones de las soluciones medidas, pierde sensibilidad progresivamente y su curva de respuesta se desplaza. Un pHmetro con cuatro semanas de uso intensivo puede leer hasta 0.3–0.5 unidades fuera del valor real en el rango ácido (5.5–6.5), que es precisamente el rango crítico del cultivo.

La calibración con buffers de pH conocido (4.0 y 7.0 son los estándar) obliga al instrumento a ajustar su ecuación de respuesta comparando su lectura con el valor de referencia. Después de calibrar, el instrumento sabe dónde está su ''cero'' para cada punto de la curva.

El problema de la deriva gradual es que el valor siempre parece razonable — un instrumento descalibrado nunca marca pH 2 ni pH 12. Marca 6.3 cuando el pH real es 5.9, o 6.8 cuando es 6.4. Esas diferencias parecen menores pero producen cambios de disponibilidad de nutrientes que se acumulan durante semanas.',
  'Cadena causa → efecto → error silencioso',
  '["pH real de la solución: 5.7 → pHmetro con deriva de +0.4 en rango ácido → lectura: 6.1 → decisión: ''pH dentro del rango óptimo, no ajustar'' → raíces en pH 5.7 durante semanas → absorción de calcio y magnesio progresivamente comprometida","Síntomas de deficiencia de Ca/Mg aparecen → cultivador agrega Cal-Mag → EC del sustrato sube → diagnóstico incorrecto construido sobre un dato incorrecto","Calibración con buffers 4 y 7 → instrumento ajustado → lectura real pH 5.7 identificada → corrección simple del pH resuelve lo que parecía una deficiencia"]'::jsonb,
  'Hipótesis a descartar',
  'Que si el instrumento ''parece funcionar bien'' (muestra valores dentro de rangos razonables), no necesita calibración. El rango de deriva habitual (0.2–0.5 unidades) es completamente invisible a simple vista. Solo se detecta comparando la lectura con una solución de referencia conocida.',
  'Regla práctica: calibrar antes de decisiones importantes, después de medir soluciones muy ácidas o muy concentradas, y al menos una vez por semana en cultivos activos. Los buffers de pH son el costo de tener datos confiables, no un gasto prescindible.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  20,
  'Agua de red vs ósmosis: por qué el punto de partida define lo que podés lograr',
  'Agua base + impacto en pH/EC',
  'Variable base del sistema',
  'Comprender que la calidad del agua de partida es una variable del sistema que no se puede ignorar, y que su pH, EC y contenido de carbonatos afectan el comportamiento de toda la solución nutritiva.',
  'Error frecuente',
  'Asumir que el agua de la red es ''neutra'' y que el pH y la EC comienzan en cero al preparar el reservorio. El agua de red en Argentina tiene en general pH entre 7.0 y 8.5 y EC entre 0.3 y 0.8 mS/cm. Esos valores son la línea de base, no el cero.',
  'Qué ocurre realmente',
  'El agua de red contiene carbonatos y bicarbonatos (HCO₃⁻) disueltos, que actúan como buffer de pH. Esto significa que el agua resiste los cambios de pH: cuando se agrega ácido para bajar el pH de 7.5 a 6.0, los bicarbonatos consumen parte del ácido antes de que el pH baje. El pH cae inicialmente, pero con el tiempo los bicarbonatos restantes vuelven a subirlo.

Esto explica un fenómeno común: el cultivador ajusta el pH a 6.0 el día del riego, pero al segundo día el pH del reservorio está en 6.8 o 7.0 sin que nadie haya agregado nada. Los carbonatos no se eliminan ajustando el pH — se eliminan con agua de osmosis inversa, que tiene HCO₃⁻ prácticamente en cero.

La EC del agua de red también es una variable base. Si el agua de red tiene EC 0.5 mS/cm y la planta necesita EC 1.8 mS/cm, solo quedan 1.3 mS/cm de ''espacio'' para agregar fertilizante. Con agua de osmosis (EC ≈ 0.0), el cultivador parte de cero y tiene control total sobre la composición.',
  'Cadena causa → efecto → síntoma observable',
  '["Agua de red con pH 7.8 → agrega nutrientes → pH baja a 6.9 con ácido → 24 hs después: pH 7.4 (carbonatos rebufferizan) → clorosis intervenal en hojas nuevas (Fe, Mn, Zn bloqueados)","Diagnóstico incorrecto: agrega quelatos de Fe → mejora transitoria → pH sube de vuelta → síntoma reaparece → ciclo repetido sin solución estructural","Con agua de osmosis: pH base ≈ 6.5–7.0, EC ≈ 0.0, sin carbonatos → ajuste de pH estable, sin rebuffering → control total de la solución nutritiva"]'::jsonb,
  'Hipótesis a descartar',
  'Que el agua de ósmosis es solo para situaciones extremas o para cultivadores avanzados. El acceso a agua de baja EC y sin carbonatos no elimina la necesidad de medir — la amplifica, porque cada variable ahora depende exclusivamente del cultivador, no del agua de red que buffereaba algunos errores.',
  'La calidad del agua de partida no es un detalle técnico menor. Define el rango de lo que podés controlar. El cultivador que sabe qué tiene en su agua de red puede compensarlo. El que no lo sabe opera con una variable oculta que explica resultados que parecen inexplicables.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  21,
  'Qué registrar: el conjunto mínimo de datos que hace útil llevar un cuaderno',
  'Registro + decisión informada',
  'Disciplina técnica',
  'Identificar los datos mínimos que, registrados de forma consistente, permiten detectar tendencias, comparar ciclos y comunicar el estado del cultivo sin depender de la memoria.',
  'Error frecuente',
  'No registrar nada y confiar en la memoria para reconstruir el historial del cultivo. La memoria comprime, reorganiza y llena lagunas de forma automática. Dos semanas después, lo que ''pasó'' es una versión editada de lo que realmente ocurrió.',
  'Qué ocurre realmente',
  'El registro sirve para dos cosas que la memoria no puede hacer: detectar tendencias y comparar ciclos.

Una tendencia requiere al menos tres puntos de datos del mismo tipo en el tiempo. Un único valor de pH dice si el pH está dentro del rango. Una serie de valores de pH en días consecutivos dice si está estable, subiendo o bajando — y a qué velocidad. La tendencia es la información accionable.

Comparar ciclos requiere haber registrado qué se hizo y qué ocurrió. Sin ese registro, cada cultivo empieza desde cero. Con él, el cultivador puede reproducir lo que funcionó y evitar lo que falló.

El conjunto mínimo que hace útil un registro es el que captura las variables que más cambian en el tiempo y que más impactan en el sistema: pH, EC, temperatura del agua, temperatura ambiente y humedad relativa. Con esos cinco datos tomados con consistencia, es posible reconstruir el estado del sistema en cualquier punto del ciclo.',
  'Cadena causa → efecto → diferencia diagnóstica',
  '["Sin registro: crisis de pH aparece ''de repente'' en semana 3 → sin historial → diagnóstico desde cero → tiempo perdido y daño acumulado","Con registro: pH semana 1: 6.1, semana 2: 6.4, semana 3: 6.8 → tendencia identificada antes de los síntomas → corrección anticipada en semana 2.5 → sin crisis","Con registro de ciclos: en el ciclo anterior el pH también subió en semana 3 → patrón identificado → en el ciclo actual la corrección se anticipa desde semana 2"]'::jsonb,
  'Hipótesis a descartar',
  'Que registrar es para cultivadores avanzados o para cultivos comerciales. El registro mínimo (5 variables, 2–3 veces por semana, con fecha) lleva menos de dos minutos. El costo de no hacerlo es perder la capacidad de distinguir un problema nuevo de uno recurrente.',
  'El registro más útil no es el más completo — es el más consistente. Cinco variables dos veces por semana, durante un ciclo completo, producen más información diagnóstica que cien mediciones dispersas sin formato ni regularidad.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  22,
  'Frecuencia mínima de medición: cuándo medir para que los datos sean útiles',
  'Consistencia de medición',
  'Estabilidad como práctica',
  'Determinar la frecuencia mínima de medición que permite detectar desvíos antes de que generen síntomas, sin caer en el exceso de medición que produce ruido sin información adicional.',
  'Error frecuente',
  'Medir solo cuando hay un problema visible. Este modelo reactivo garantiza que siempre se detecta el problema tarde: los síntomas aparecen después de que la variable lleva días o semanas fuera del rango óptimo.',
  'Qué ocurre realmente',
  'Los problemas de cultivo no aparecen de golpe. Aparecen como desvíos graduales que se acumulan hasta superar el umbral de síntoma visible. Un pH que sube 0.15 unidades por día pasa de 6.0 a 7.0 en menos de una semana. Las primeras señales de bloqueo de absorción aparecen cuando ya llevan tres o cuatro días sobre 6.8.

La frecuencia de medición define el margen de reacción disponible. Con medición diaria, un pH de 6.7 detectado hoy permite una corrección simple mañana. Con medición semanal, el pH puede estar en 7.5 cuando se detecta — la corrección es más brusca y la planta ya tiene síntomas.

Sin embargo, medir con demasiada frecuencia (varias veces al día) no agrega información porque el sistema no cambia tan rápido. La variabilidad de lecturas cercanas en el tiempo refleja más el error de medición que cambios reales en el sistema.',
  'Cadena causa → efecto → margen de corrección',
  '["Medición semanal: pH lunes 6.1 → desvío silencioso → pH domingo 7.3 → síntomas aparecen → corrección necesaria: bajar 1.2 unidades → estrés por ajuste brusco","Medición cada 2–3 días: pH lunes 6.1 → pH miércoles 6.5 → pH viernes 6.9 → sin síntomas aún → corrección: bajar 0.4 unidades → sin estrés adicional","Medición diaria en primera semana de ciclo: detecta patrones de subida o bajada específicos del lote o del agua → calibra el plan de frecuencia para el resto del ciclo"]'::jsonb,
  'Hipótesis a descartar',
  'Que medir más frecuentemente es siempre mejor. La medición diaria en ciclos estables produce lecturas muy similares entre sí — la variación entre días consecutivos está dentro del margen de error del instrumento. Esa densidad de datos no mejora las decisiones; solo aumenta el tiempo invertido.',
  'Frecuencia práctica: diaria o cada 2 días durante el primer mes de un ciclo nuevo (hasta conocer el comportamiento del sistema), y cada 2–3 días en ciclos estables. Ajustar si se cambia de agua, fertilizante o sustrato — las transiciones son los momentos de mayor variabilidad.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  23,
  'Cómo leer tus propios datos: convertir mediciones en tendencias accionables',
  'Análisis básico de tendencias',
  'Lectura histórica básica',
  'Interpretar una serie de mediciones propias para identificar tendencias (estable, subiendo, bajando), estimar hacia dónde va el sistema y anticipar correcciones antes de que aparezcan síntomas.',
  'Error frecuente',
  'Registrar datos sin revisarlos en contexto. El cultivador anota pH 6.1, pH 6.3, pH 6.5 en días sucesivos y cada vez que mide solo pregunta ''¿está dentro del rango?''. No pregunta ''¿hacia dónde se mueve?''.',
  'Qué ocurre realmente',
  'Un valor de pH aislado responde a la pregunta ''¿cómo está el sistema ahora?''. Una serie de valores responde a la pregunta más útil: ''¿hacia dónde va el sistema?''.

La tendencia es el patrón de cambio en el tiempo. Para identificarla, se necesitan al menos tres puntos consecutivos de la misma variable. Con tres puntos es posible determinar la dirección (sube, baja, estable) y la velocidad (cuánto cambia por día o por riego).

Con la velocidad de cambio, el cultivador puede estimar cuándo el sistema llegará a un umbral problemático. Si el pH sube 0.2 unidades cada dos días y está en 6.4 hoy, llegará a 7.0 en seis días. Esa estimación permite actuar antes del umbral, con una corrección pequeña, en lugar de reaccionar después, con una corrección grande.

El análisis básico no requiere herramientas complejas. Tres valores en una tabla, una resta para calcular la diferencia entre mediciones y una división para obtener la tasa de cambio es suficiente.',
  'Cadena causa → efecto → ventaja diagnóstica',
  '["Registro: pH día 1: 6.0, día 3: 6.3, día 5: 6.6 → diferencia promedio: +0.15 por día → proyección: llegará a 7.0 en día 7.6 → corrección anticipada en día 6 (baja pH 0.3 unidades) → sin síntomas","Sin tendencia: pH día 5: 6.6 → ''todavía en rango'' → no corrige → día 7: pH 7.0 → día 9: síntomas de clorosis → corrección tardía","EC: día 1: 1.6, día 5: 2.1, día 10: 2.7 → tasa de subida: +0.11 mS/cm por día → indica acumulación de sales → programar lavado antes de llegar a 3.5"]'::jsonb,
  'Hipótesis a descartar',
  'Que analizar tendencias requiere muchos datos o herramientas especiales. Tres mediciones consecutivas son suficientes para identificar una tendencia. El análisis puede hacerse con lápiz y papel — la tasa de cambio es una resta y una división. La complejidad no está en el cálculo sino en el hábito de hacer la pregunta correcta: no ''¿está bien hoy?'' sino ''¿hacia dónde va?''.',
  'Tres mediciones es una tendencia. Cinco es un patrón. Diez es el comportamiento característico de tu sistema con tu agua, tu sustrato y tu fertilizante. Esa información vale más que cualquier guía genérica porque está calibrada a tu cultivo específico.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  24,
  'pH, EC y VPD: las tres variables que no se pueden gestionar por separado',
  'pH + EC + VPD',
  'Pensamiento sistémico completo',
  'Comprender que pH, EC y VPD forman un sistema de variables interdependientes y que ajustar una sin considerar las otras produce resultados impredecibles.',
  'Error frecuente',
  'Ajustar el pH a 6.0, luego la EC a 2.0 y luego el VPD a 1.2 kPa en sesiones distintas, sin verificar cómo cada corrección afecta a las otras. El sistema se modifica como si fuera un tablero con controles independientes — y no lo es.',
  'Qué ocurre realmente',
  'El pH, la EC y el VPD no son variables paralelas: se afectan mutuamente a través de la planta.

El VPD controla la velocidad de transpiración y por tanto el flujo de agua a través de la planta. Ese flujo arrastra calcio desde la raíz hacia las hojas jóvenes. Si el VPD es demasiado bajo, el flujo se detiene y el calcio no llega aunque la EC del sustrato sea correcta.

La EC del sustrato afecta la cantidad de agua que la raíz puede absorber. Una EC alta invierte el gradiente osmótico y reduce la absorción hídrica — lo que también afecta el transporte de calcio que depende del flujo de agua.

El pH controla qué iones están disponibles para ser transportados. Un pH que deriva mientras se ajustan EC y VPD puede dejar sin sentido ambas correcciones: los nutrientes presentes simplemente no son absorbibles.

El resultado es que tres variables dentro de su rango individual pueden producir deficiencias visibles porque su combinación crea condiciones que ninguna de las tres refleja por separado.',
  'Cadena de interacción sistémica',
  '["VPD 0.6 kPa (frío y húmedo) + EC 1.8 correcta + pH 6.2 correcto → transpiración mínima → flujo de xilema detenido → calcio no se mueve → tip burn en hojas jóvenes aunque las tres variables estén ''en rango''","VPD 1.2 kPa normalizado → flujo de xilema activo → calcio transportado → tip burn desaparece sin cambiar EC ni pH","pH 7.1 + EC correcta + VPD correcto → Fe, Mn y Zn bloqueados → clorosis intervenal aunque el fertilizante sea correcto"]'::jsonb,
  'Hipótesis a descartar',
  'Que si las tres variables están dentro de su rango individual, el sistema funciona correctamente. El rango de cada variable se define con las otras en condiciones estándar. En la práctica, la interacción entre ellas puede crear combinaciones problemáticas que ningún rango individual anticipa.',
  'El sistema de cultivo es un sistema — no un tablero de parámetros independientes. Cuando aparece un síntoma inexplicable con todas las variables ''en rango'', el paso siguiente no es medir más variables: es analizar cómo las que ya tenés se están afectando entre sí.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  25,
  'El ciclo de vida del pH en el sustrato: cómo deriva y cómo anticiparlo',
  'pH + tiempo + carbonatos',
  'Gestión dinámica del pH',
  'Comprender que el pH del sustrato no se mantiene estable entre riegos sino que deriva de forma predecible, y que esa deriva puede anticiparse y corregirse antes de que produzca síntomas.',
  'Error frecuente',
  'Ajustar el pH en el reservorio antes de regar y asumir que ese pH se mantiene en el sustrato hasta el próximo riego. El pH medido el día del riego no es el pH que las raíces experimentan tres días después.',
  'Qué ocurre realmente',
  'El pH en el sustrato cambia entre riegos por tres mecanismos simultáneos.

Primero, la actividad radicular. Las raíces absorben iones del sustrato de forma selectiva. Cuando absorben más cationes (NH₄⁺, K⁺, Ca²⁺) que aniones, liberan H⁺ al sustrato para mantener el equilibrio electroquímico — esto baja el pH. Cuando absorben más aniones (NO₃⁻, H₂PO₄⁻), liberan OH⁻ o HCO₃⁻ — esto sube el pH.

Segundo, los carbonatos residuales del agua. Si el agua de riego contiene carbonatos y bicarbonatos, estos se acumulan en el sustrato entre riego y riego. Los bicarbonatos tienen capacidad buffer y elevan el pH gradualmente hasta que el siguiente riego lo baja de nuevo.

Tercero, la actividad microbiana. Los microorganismos del sustrato producen CO₂ durante su actividad metabólica. Al disolverse en el agua del sustrato forma ácido carbónico y baja el pH.

El resultado es que el pH describe una curva entre riegos, no un valor estable. La amplitud de esa curva depende del tipo de sustrato, la calidad del agua y la carga nutritiva.',
  'Patrón de deriva entre riegos',
  '["Día riego: pH ajustado a 6.0 en reservorio → raíces reciben pH ~6.0","Día +1: actividad radicular + bicarbonatos del agua → pH sustrato sube a 6.4","Día +2: acumulación de carbonatos + VPD alto → pH sustrato 6.8","Día +3: pH 7.1 → absorción de Fe, Mn, Zn bloqueada → inicio de clorosis aunque el último riego era ''correcto''"]'::jsonb,
  'Hipótesis a descartar',
  'Que el pH del runoff refleja el pH del reservorio de ese día. El runoff refleja el estado del sustrato, no del agua de entrada. Si el pH del runoff es consistentemente más alto que el pH del reservorio, los carbonatos se están acumulando — y ajustar solo el reservorio no lo resuelve sin cambiar también la calidad del agua base.',
  'El pH que importa es el que las raíces experimentan entre riegos, no el del momento del riego. Medir el runoff después de cada riego y compararlo con el pH de entrada convierte la deriva de pH en una variable observable, no en una sorpresa.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  26,
  'EC acumulativa: por qué el sustrato envejece con cada riego',
  'EC + riegos + acumulación de sales',
  'Gestión de ciclo',
  'Comprender que la EC del sustrato no refleja la EC del agua de riego sino la acumulación de sales de todos los riegos anteriores, y que esa acumulación es predecible y gestionable si se mide.',
  'Error frecuente',
  'Regar siempre con la misma EC en el reservorio y asumir que la EC del sustrato es igual a la del agua de entrada. La EC del runoff es el dato real del sustrato — y casi siempre es más alta que la EC de entrada.',
  'Qué ocurre realmente',
  'Cuando se riega, el agua de entrada disuelve las sales del sustrato y las arrastra hacia afuera como runoff. Pero el proceso no es perfecto: una fracción de las sales siempre queda retenida en las zonas de menor drenaje del sustrato. Con cada riego, esa fracción se acumula.

Además, la planta absorbe agua y nutrientes de forma selectiva. Absorbe más agua que nutrientes en proporción, lo que concentra progresivamente las sales en el agua restante del sustrato.

El efecto combinado es que la EC del sustrato sube de forma gradual a lo largo del ciclo, independientemente de si la EC del reservorio se mantiene constante. En sustratos con poco drenaje o en ciclos de más de 8 semanas, la EC de la zona radicular puede ser hasta 1.5–2 veces la EC del reservorio.

Este proceso es medible: la diferencia entre EC del runoff y EC de entrada es el indicador clave. Cuando esa diferencia supera 0.5–0.8 mS/cm de forma sostenida, el sustrato necesita un lavado preventivo.',
  'Cadena de acumulación a lo largo del ciclo',
  '["Semana 1: EC entrada 1.8, EC runoff 2.0 → diferencia 0.2 → normal","Semana 3: EC entrada 1.8, EC runoff 2.5 → diferencia 0.7 → acumulación activa","Semana 5: EC entrada 1.8, EC runoff 3.2 → diferencia 1.4 → estrés osmótico incipiente → bordes foliares quemados aunque la nutrición del reservorio sea correcta","Lavado con agua baja EC → runoff baja a 1.5 → acumulación reiniciada desde cero"]'::jsonb,
  'Hipótesis a descartar',
  'Que un runoff con EC alta indica que se está abonando de más. El runoff refleja el historial de riegos, no el riego del día. Un runoff de 3.0 con reservorio de 1.8 indica acumulación histórica, no sobredosis actual. La respuesta correcta es el lavado, no reducir la EC del reservorio.',
  'La EC del runoff es la memoria del sustrato. Medirla después de cada riego y registrar la diferencia respecto a la EC de entrada convierte la acumulación en un parámetro monitoreable. La acumulación no es un accidente — es la consecuencia predecible de regar, y se gestiona con lavados planificados.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  27,
  'Lavados preventivos: cómo programarlos antes de que sean urgentes',
  'EC + frecuencia + volumen de lavado',
  'Planificación',
  'Diseñar un protocolo de lavado preventivo basado en los datos de EC del runoff, de forma que los lavados se realicen antes de que la acumulación de sales produzca síntomas.',
  'Error frecuente',
  'Hacer el primer lavado del ciclo cuando ya hay síntomas de quemaduras o estrés osmótico. Un lavado en crisis requiere volúmenes mayores, produce un cambio brusco en las condiciones del sustrato y es más difícil de controlar que un lavado planificado.',
  'Qué ocurre realmente',
  'Un lavado preventivo es un riego con agua de baja EC y alto volumen de runoff (40–50% del volumen aplicado) destinado a arrastrar sales acumuladas antes de que generen estrés.

La diferencia entre un lavado preventivo y uno de emergencia es el estado de partida. En el preventivo, el sustrato tiene EC elevada pero la planta no tiene síntomas. El objetivo es bajar la EC de la zona radicular al rango objetivo con 1–2 riegos. El sistema se estabiliza rápido porque no hay daño radicular que reparar.

En el lavado de emergencia hay síntomas activos (bordes quemados, turgor bajo, clorosis). El sustrato tiene EC muy alta y las raíces tienen daño osmótico. La recuperación es más lenta y no siempre completa si el daño fue prolongado.

El criterio para programar el lavado preventivo es la diferencia EC runoff - EC entrada. Cuando esa diferencia supera 0.5 mS/cm de forma consistente (dos mediciones consecutivas), es el momento óptimo para actuar.',
  'Protocolo de lavado preventivo',
  '["Detección: EC runoff > EC entrada + 0.5 mS/cm por segunda medición consecutiva → programar lavado en próximo riego","Lavado: agua a EC baja (0.3–0.5 mS/cm) + volumen normal × 1.5 → runoff objetivo: 40–50% del volumen aplicado","Verificación: medir EC del runoff al inicio, mitad y final del lavado → la EC del runoff debe bajar progresivamente","Post-lavado: retomar EC normal del reservorio → medir EC del runoff 24–48 hs después → confirmar estabilización"]'::jsonb,
  'Hipótesis a descartar',
  'Que lavar el sustrato elimina los nutrientes y la planta queda sin alimentación. El lavado elimina el exceso de sales acumuladas, pero el efecto es temporal y controlado. Después del lavado, la planta recibe el agua de reservorio con la EC correcta y la absorción se normaliza. Una planta con EC radicular alta no absorbe bien aunque haya nutrientes disponibles.',
  'Un lavado preventivo cada 3–4 semanas en ciclos largos, guiado por los datos de EC del runoff, es más efectivo que tres lavados de emergencia en crisis. El costo del agua y el tiempo del lavado es menor que el costo del daño acumulado.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  28,
  'Señales de alerta temprana: detectar problemas en los datos antes de que lleguen a la hoja',
  'Datos + tendencia + umbral de alerta',
  'Anticipación preventiva',
  'Identificar los patrones en los registros de medición que preceden a los síntomas visibles, y actuar sobre esos patrones antes de cruzar el umbral de síntoma.',
  'Error frecuente',
  'Usar los datos como confirmación del estado actual en lugar de como predictor del estado futuro. El cultivador mide, anota ''6.8 — ok'' y no hace la pregunta que haría diferencia: ''¿a este ritmo, cuándo llega a 7.2?''.',
  'Qué ocurre realmente',
  'Los síntomas visibles no aparecen cuando la variable cruza el umbral — aparecen días después de que la variable lleva tiempo fuera del rango. Un pH de 7.2 no produce clorosis intervenal el mismo día; la clorosis aparece cuando los tejidos formados durante los días de pH elevado finalmente se hacen visibles.

Esto crea una ventana: entre el momento en que la variable cruza el umbral y el momento en que el síntoma es visible, existe un período donde la corrección es simple y el daño es reversible. Los datos son la única herramienta que permite actuar en esa ventana.

Las señales de alerta temprana son cambios en la tasa de variación, no en el valor absoluto. Un pH de 6.7 que estuvo en 6.5 hace dos días y en 6.3 hace cuatro días es una señal de alerta aunque el valor actual esté ''en rango''. La tasa de cambio (+0.2 unidades cada dos días) predice que llegará a 7.1 en cuatro días más.

Lo mismo aplica a la EC del runoff, la HR y la temperatura del canopy: cualquier variable que muestre una tendencia sostenida hacia el umbral es una señal de alerta, independientemente del valor del día.',
  'Detección de señal de alerta vs síntoma',
  '["pH día 1: 6.2 → día 3: 6.5 → día 5: 6.8 → tasa: +0.15/día → proyección: pH 7.1 en día 7 → alerta activa en día 5","Acción anticipada (día 5): ajuste de pH + revisión de agua base → pH estabilizado en 6.3 → sin síntomas","Sin alerta: día 7 pH 7.1 → día 9 síntomas de clorosis en hojas nuevas → corrección tardía + 5–7 días de recuperación"]'::jsonb,
  'Hipótesis a descartar',
  'Que si el valor de hoy está dentro del rango, no hay nada que hacer. El rango define un límite estático. La tendencia define la trayectoria del sistema. Un valor dentro del rango con tendencia acelerada hacia el límite tiene menos margen de corrección que un valor fuera del rango con tendencia estable o revertiendo.',
  'La anticipación no es paranoia — es lo que distingue al cultivador que gestiona el sistema del que reacciona a él. Los datos registrados de forma consistente convierten el cultivo en un sistema predecible, no en una serie de emergencias.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  29,
  'Estabilizar el ambiente antes de la floración: la transición que no se improvisa',
  'Temperatura + humedad + VPD por fase',
  'Transición de fase',
  'Planificar el ajuste de VPD, temperatura y humedad en la semana de transición al fotoperiodo 12/12, para que el sistema ambiental esté estable antes de que la planta empiece a desarrollar flores.',
  'Error frecuente',
  'Cambiar el fotoperiodo a 12/12 sin modificar los parámetros ambientales. La planta entra en floración con el ambiente de vegetativo, que tiene rangos distintos a los que optimizan la fase reproductiva.',
  'Qué ocurre realmente',
  'La fase de floración tiene requerimientos ambientales distintos a la vegetativa, principalmente por dos razones.

Primero, el riesgo de botrytis (moho gris) aumenta en floración tardía porque la densidad de las flores crea microambientes de baja circulación y alta HR localizada. La HR objetivo en floración avanzada (semanas 6–12) es de 40–50%, significativamente más baja que el 60–70% óptimo en vegetativo.

Segundo, el VPD óptimo cambia porque la arquitectura de la planta cambia. Las flores generan menos transpiración por unidad de superficie que las hojas. El mismo VPD que producía flujo de xilema activo en vegetativo puede ser insuficiente en floración para mover calcio a las flores jóvenes.

El momento óptimo para ajustar estos parámetros es la semana previa al cambio de fotoperiodo: los ajustes se hacen con la planta en vegetativo, que es más tolerante al cambio, y la floración comienza con el ambiente ya estable.',
  'Protocolo de transición ambiental',
  '["Semana –1 (antes del 12/12): bajar HR gradualmente de 65% a 55% → ajustar temperatura nocturna a 18–20°C → verificar VPD resultante","Semana 1 floración: HR 55%, temperatura día 24–26°C, noche 18–20°C → VPD 0.9–1.2 kPa → condiciones estables desde el inicio","Semana 6–8 floración: HR 45–50%, temperatura día 22–24°C → reducción de riesgo de botrytis en flores densas","Sin ajuste previo: cambio brusco de HR en semana 3 con flores en desarrollo → estrés por cambio ambiental en planta con alta demanda metabólica"]'::jsonb,
  'Hipótesis a descartar',
  'Que el diferencial de temperatura día–noche es solo para aumentar los colores de las flores. El diferencial térmico tiene efecto real sobre el perfil de terpenos y la expresión de antocianinas, pero su función primaria es el control del VPD nocturno y la gestión del crecimiento internodal. Es una variable técnica antes de ser estética.',
  'La calidad de la floración se construye desde la semana –1. El ambiente que recibe la planta el primer día de 12/12 define las condiciones de desarrollo de las flores de las próximas ocho semanas. Ajustar el ambiente cuando ya hay flores establecidas implica corregir un proceso en marcha — siempre es más difícil que prevenir.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  30,
  'El runoff como instrumento: qué dice la solución de salida sobre la zona radicular',
  'EC runoff vs EC entrada + pH runoff',
  'Diagnóstico de zona radicular',
  'Interpretar los datos de EC y pH del runoff para obtener información sobre el estado del sustrato y la zona radicular que no puede obtenerse midiendo solo el agua de entrada.',
  'Error frecuente',
  'Medir solo el agua de entrada al reservorio y asumir que el estado del sustrato es igual al del reservorio. El sustrato puede tener una EC dos veces mayor que el reservorio sin que el cultivador lo sepa si no mide el runoff.',
  'Qué ocurre realmente',
  'El runoff es la solución que ha estado en contacto con las raíces y con el sustrato acumulado. Contiene información que el agua de entrada no tiene: el estado real del pH y la EC en la zona donde ocurre la absorción.

La comparación entre agua de entrada y runoff produce dos indicadores clave.

EC runoff - EC entrada: la diferencia representa la acumulación de sales en el sustrato. Una diferencia positiva sostenida indica que el sustrato se está concentrando. Una diferencia que supera 0.5 mS/cm de forma consistente es la señal para programar un lavado preventivo.

pH runoff vs pH entrada: si el runoff tiene pH consistentemente más alto que la entrada, los carbonatos del agua se están acumulando o la actividad radicular está liberando OH⁻. Si el runoff tiene pH más bajo, la actividad radicular está liberando H⁺ (absorción predominante de cationes — normal en etapas de crecimiento activo).

El volumen de runoff también importa. Con buen drenaje, el 15–20% del volumen de riego debe salir como runoff. Si el runoff es inferior al 10%, el sustrato tiene dificultades de drenaje y las sales se están concentrando más rápido.',
  'Lectura de runoff post-riego',
  '["EC entrada: 1.8, EC runoff: 2.4 → diferencia: 0.6 → acumulación moderada → planificar lavado en 2–3 riegos","pH entrada: 6.0, pH runoff: 6.8 → diferencia: +0.8 → carbonatos activos en sustrato → evaluar calidad de agua o cambiar a ósmosis","EC entrada: 1.8, EC runoff: 3.6 → diferencia: 1.8 → acumulación severa → lavado inmediato antes del próximo riego regular","Volumen runoff < 10% → drenaje insuficiente → acumulación acelerada → revisar composición del sustrato"]'::jsonb,
  'Hipótesis a descartar',
  'Que un runoff con EC alta después de un lavado indica que el lavado fue insuficiente. El runoff siempre tiene EC mayor que el agua de entrada cuando hay acumulación — eso es el mecanismo del lavado, no su fracaso. Lo que indica el éxito es que la EC del runoff baja progresivamente durante el lavado y se estabiliza cerca de la EC de entrada al final.',
  'El runoff es la voz del sustrato. Medir EC y pH del runoff después de cada riego lleva dos minutos y produce el dato más valioso del sistema: el estado real de la zona donde ocurre la absorción, no el estado del reservorio.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  31,
  'Temperatura foliar vs temperatura ambiente: por qué el termómetro de pared no es suficiente',
  'Temperatura foliar + VPD real',
  'Medición avanzada',
  'Comprender que la temperatura del canopy puede diferir significativamente de la temperatura ambiente, y que esa diferencia modifica el VPD real que experimenta la planta independientemente del VPD calculado con datos del cuarto.',
  'Error frecuente',
  'Calcular el VPD con la temperatura y HR del aire sin verificar si la temperatura foliar coincide con la ambiental. En condiciones de alta intensidad lumínica o baja circulación de aire, la hoja puede estar varios grados más caliente que el ambiente, produciendo un VPD real significativamente mayor que el calculado.',
  'Qué ocurre realmente',
  'La temperatura foliar es el resultado del balance energético de la hoja: la energía que entra (luz absorbida, temperatura del aire) menos la energía que sale (transpiración, reflexión, re-emisión infrarroja).

Cuando la transpiración es activa, la evaporación del agua en los estomas tiene efecto refrigerante y mantiene la temperatura foliar 1–3°C por debajo de la temperatura del aire circundante.

Pero cuando la circulación de aire es insuficiente o la intensidad lumínica es muy alta, la hoja absorbe más energía de la que puede disipar mediante transpiración. La temperatura foliar sube por encima de la temperatura ambiente. Con una lámpara LED de alta potencia y circulación insuficiente, la diferencia puede ser de 4–6°C.

Esta diferencia importa porque el VPD se calcula con la temperatura foliar, no con la temperatura ambiente. Una hoja a 30°C con HR 55% tiene VPD 2.1 kPa — estrés por transpiración excesiva. Si el termómetro de pared marcaba 25°C con la misma HR, el VPD calculado sería 1.3 kPa — aparentemente en rango. La planta está estresada aunque el ''VPD del cuarto'' lo ignore.',
  'Diagnóstico con termómetro infrarrojo',
  '["Termómetro pared: 25°C, HR: 55% → VPD calculado: 1.3 kPa → decisión: ''ok''","Termómetro IR sobre canopy: 30°C → VPD real: 2.1 kPa → estrés hídrico foliar no detectado con termómetro de pared","Hojas enrolladas hacia arriba en las zonas más cercanas a la lámpara → confirma estrés térmico localizado","Solución: aumentar circulación de aire sobre el canopy → temperatura foliar baja 2–3°C → VPD se normaliza sin cambiar temperatura del cuarto"]'::jsonb,
  'Hipótesis a descartar',
  'Que el termómetro infrarrojo es solo para setups avanzados. Es el instrumento más informativo para calibrar la temperatura real del canopy. El costo de no tenerlo es operar con un VPD calculado que puede estar sistemáticamente desviado del VPD real que experimenta la planta.',
  'La temperatura que importa para el VPD es la de la hoja, no la del cuarto. La diferencia entre ambas puede ser de 0 o de 6°C dependiendo de la circulación y la intensidad lumínica. Solo el termómetro infrarrojo puede medir esa diferencia.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  32,
  'Construir un protocolo de diagnóstico propio: el sistema que trabaja sin improvisar',
  'Variables + orden + criterio documentado',
  'Sistematización del diagnóstico',
  'Diseñar un protocolo de diagnóstico personal que defina el orden de verificación de variables, los umbrales de acción y el criterio para cerrar cada hipótesis, produciendo diagnósticos consistentes independientemente del estado emocional del cultivador.',
  'Error frecuente',
  'Diagnosticar por intuición y experiencia sin un proceso documentado. El diagnóstico intuitivo funciona en condiciones conocidas pero falla en condiciones nuevas, bajo presión o después de un período de ausencia.',
  'Qué ocurre realmente',
  'Un protocolo de diagnóstico es una secuencia de preguntas ordenadas que reduce el espacio de hipótesis posibles de forma eficiente. No reemplaza el criterio del cultivador — lo hace reproducible.

La secuencia debe ordenar las verificaciones por tres criterios combinados: velocidad (cuánto tiempo lleva medir), relevancia (qué probabilidad tiene esa variable de ser la causa) e impacto (qué tan grave es si no se detecta).

Un protocolo efectivo tiene cuatro componentes: el árbol de preguntas (qué verifico primero, segundo, tercero), los umbrales de acción (a qué valor de pH actúo, no ''cuando sea necesario''), el criterio de cierre de hipótesis (cómo sé que descarté esta variable de forma válida) y el registro de decisiones (qué hice, qué mejoró, qué empeoró).

El registro de decisiones convierte cada ciclo en información para el siguiente. Un protocolo sin registro mejora la consistencia dentro del ciclo pero no acumula aprendizaje entre ciclos.',
  'Estructura básica de protocolo',
  '["Síntoma detectado → Paso 1: verificar temperatura y HR (30 seg) → dentro de rango → descartado","→ Paso 2: medir pH del runoff (5 min) → 7.1 → fuera de rango → hipótesis activa: pH bloqueante","→ Paso 3: ajustar pH, documentar fecha, valor antes y después, síntoma observado","→ Paso 4 (48 hs): ¿mejoró el síntoma? → sí → causa confirmada, registrar en historial del ciclo","→ Paso 4 (48 hs): ¿sin cambio? → hipótesis incorrecta → reactivar desde el siguiente paso del protocolo"]'::jsonb,
  'Hipótesis a descartar',
  'Que un protocolo de diagnóstico es necesario solo para cultivadores nuevos o para cultivos comerciales. La experiencia no elimina la necesidad del protocolo — la sofistica. El cultivador experimentado tiene un protocolo implícito que opera sin conciencia de que existe. Hacerlo explícito elimina los pasos redundantes y asegura que los pasos críticos no se salteen bajo presión.',
  'Un protocolo escrito no es un manual de instrucciones — es la destilación del criterio propio en una forma reproducible. Cada ciclo en que se sigue el protocolo y se registra el resultado lo mejora. Después de tres o cuatro ciclos, el protocolo ya no es una ayuda externa: es el criterio propio documentado.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  33,
  'Deficiencias primarias y secundarias: cómo distinguirlas antes de tratarlas',
  'Movilidad de nutrientes + pH + síntoma',
  'Diagnóstico diferencial',
  'Distinguir si una deficiencia visible es primaria (el nutriente no está disponible en el sustrato) o secundaria (el nutriente está disponible pero no puede absorberse por una causa externa), porque el tratamiento correcto es completamente diferente en cada caso.',
  'Error frecuente',
  'Tratar toda deficiencia visual agregando el nutriente que parece faltar. Si la deficiencia es secundaria — causada por pH incorrecto, estrés osmótico o daño radicular — agregar más del nutriente no resuelve nada: la causa sigue bloqueando la absorción y la EC del sustrato sube sin beneficio.',
  'Qué ocurre realmente',
  'Una deficiencia primaria ocurre cuando el nutriente genuinamente no está presente en concentración suficiente en la solución del sustrato. La solución es agregar ese nutriente.

Una deficiencia secundaria ocurre cuando el nutriente está presente pero algo externo bloquea su absorción: pH fuera del rango de biodisponibilidad, EC alta que invierte el gradiente osmótico, oxígeno insuficiente en la zona radicular, o daño radicular previo.

La herramienta de distinción es el análisis de la causa antes de actuar:

1. Medir pH. Si está fuera del rango de disponibilidad del nutriente afectado, la deficiencia es secundaria por pH.
2. Medir EC del runoff. Si está alta (> 3.0 mS/cm), la deficiencia puede ser secundaria por estrés osmótico.
3. Verificar temperatura del agua y del ambiente. Si hay estrés térmico, la absorción está comprometida de forma sistémica.
4. Si pH, EC y temperatura están correctos, la deficiencia tiene mayor probabilidad de ser primaria.

Una clave adicional es la velocidad de aparición. Las deficiencias secundarias aparecen de forma difusa en múltiples hojas en poco tiempo. Las deficiencias primarias se desarrollan más lentamente y siguen el patrón de movilidad del nutriente (hojas viejas primero para elementos móviles, hojas nuevas para elementos inmóviles).',
  'Árbol de distinción primaria / secundaria',
  '["Clorosis intervenal en hojas nuevas → elemento inmóvil afectado (Fe, Mn, Zn, Ca) → medir pH","pH 7.2 → rango de bloqueo de Fe, Mn, Zn → deficiencia secundaria por pH → solución: corregir pH, NO agregar microelementos","pH 6.2 → fuera del rango de bloqueo → medir EC runoff: 2.2 mS/cm → normal → verificar temperatura del agua","Temperatura agua 8°C (invierno) → absorción inhibida por temperatura → deficiencia secundaria por temperatura → atemperar el agua"]'::jsonb,
  'Hipótesis a descartar',
  'Que si se agrega el nutriente que falta y el síntoma mejora, la deficiencia era primaria. Las deficiencias secundarias también pueden responder transitoriamente al agregado del nutriente afectado (especialmente con quelatos), pero el síntoma reaparece porque la causa no fue resuelta.',
  'La distinción entre primaria y secundaria no requiere análisis de agua complejo — requiere medir las variables básicas antes de actuar. pH, EC del runoff y temperatura del agua son la triada que descarta las causas secundarias más comunes en menos de diez minutos.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  34,
  'Vegetativo y floración: por qué el mismo setup no funciona en ambas fases',
  'Variables por fase del ciclo',
  'Gestión de fase',
  'Identificar los parámetros ambientales y nutricionales óptimos de cada fase y comprender por qué mantener los mismos valores durante todo el ciclo produce resultados subóptimos en al menos una de las dos fases.',
  'Error frecuente',
  'Mantener la misma temperatura, humedad, EC y perfil de nutrientes durante todo el ciclo porque ''la planta está creciendo bien''. Los parámetros que optimizan el crecimiento vegetativo no son los mismos que optimizan la producción de resinas y flores.',
  'Qué ocurre realmente',
  'Las necesidades de la planta cambian radicalmente entre la fase vegetativa y la de floración porque los procesos metabólicos activos en cada fase son distintos.

En vegetativo, el objetivo es maximizar la producción de tejido verde. Esto requiere alta demanda de nitrógeno (para síntesis de proteínas y clorofila), temperatura alta (22–26°C) y VPD moderado para sostener el flujo de xilema activo.

En floración, el objetivo cambia: producción de flores, resinas y semillas. El nitrógeno pasa a un segundo plano — su exceso incluso inhibe la floración y produce ''quemado de nitrógeno''. El fósforo y el potasio toman precedencia. La temperatura óptima baja ligeramente (20–24°C en floración tardía) porque temperaturas altas degradan terpenos. La HR debe bajar para reducir el riesgo de botrytis.

El diferencial de temperatura día-noche tiene efectos distintos según la fase: en vegetativo, un diferencial moderado (5–8°C) produce internodos compactos. En floración tardía, un diferencial más pronunciado (8–12°C) favorece la acumulación de resinas y la expresión de pigmentos en genéticas que los producen.',
  'Parámetros comparativos por fase',
  '["Vegetativo: N alto, P y K moderados → EC 1.4–1.8, temperatura 22–26°C, HR 60–70%, VPD 0.8–1.2 kPa","Semana 1–3 floración (stretch): N moderado, P y K aumentan → EC 1.8–2.2, temperatura 22–24°C, HR 55–60%","Floración media (semana 4–7): N mínimo, P y K altos → EC 2.0–2.4, temperatura 20–24°C, HR 50–55%","Floración tardía (semana 8–12): N casi nulo, flushing progresivo → EC 1.2–1.6, temperatura 18–22°C, HR 40–50%"]'::jsonb,
  'Hipótesis a descartar',
  'Que las diferencias entre fases son preferencias del cultivador y no tienen impacto medible. El exceso de nitrógeno en floración produce efectos observables documentados: hojas que mantienen verde oscuro cuando deberían estar madurando, sabor más vegetal y menor rendimiento de resinas. Son efectos medibles, no estéticos.',
  'El ciclo de cultivo no es una línea recta — es una secuencia de fases con requerimientos distintos. Gestionar el ciclo completo implica ajustar los parámetros en cada transición. El cultivador que cambia sus parámetros con el ciclo trabaja con la biología de la planta, no contra ella.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  35,
  'Nutrición de transición: cómo cambiar el perfil nutricional sin generar estrés',
  'N-P-K por fase + timing de transición',
  'Planificación de ciclo',
  'Diseñar la transición nutricional entre la fase vegetativa y la floración de forma gradual, evitando el cambio brusco de perfil que genera estrés en una planta que ya tiene alta demanda metabólica.',
  'Error frecuente',
  'Cambiar al fertilizante de floración al 100% el primer día del cambio de fotoperiodo. La planta continúa en crecimiento vegetativo activo durante la primera semana del 12/12 — el cambio brusco de perfil nutricional en ese momento genera estrés sin necesidad.',
  'Qué ocurre realmente',
  'El cambio de fotoperiodo de 18/6 a 12/12 no produce un cambio biológico inmediato. La planta detecta el cambio en el ciclo de oscuridad y comienza a producir las fitohormonas que inducen la floración. Este proceso toma varios días.

Durante la primera y segunda semana del 12/12, la planta está en transición: sigue elongando internodos y produciendo hojas (crecimiento vegetativo activo) mientras desarrolla los primordios florales. Esta fase se llama ''stretch'' y puede durar entre 7 y 21 días dependiendo de la genética.

Durante el stretch, la planta aún tiene alta demanda de nitrógeno para el crecimiento vegetativo activo. Un cambio al fertilizante de floración (bajo N, alto P y K) en ese momento genera dos problemas simultáneos: déficit de N para el crecimiento en curso, y exceso de P y K que la planta no puede usar todavía porque la floración no está activa.

La transición gradual consiste en mezclar progresivamente el fertilizante de vegetativo y el de floración durante las dos primeras semanas del 12/12, aumentando la proporción de floración a medida que el stretch se completa y los primordios florales se vuelven visibles.',
  'Protocolo de transición gradual',
  '["Día 1–7 del 12/12: 75% fertilizante vegetativo + 25% floración → planta en stretch activo → N suficiente para crecimiento","Día 7–14: 50% / 50% → stretch completando → primordios florales visibles → N moderado, P y K aumentando","Día 14–21: 25% / 75% → flores en desarrollo inicial → perfil de floración dominante con transición completada","Día 21+: 100% floración → flores establecidas → nutrición de floración completa"]'::jsonb,
  'Hipótesis a descartar',
  'Que el fertilizante de floración activa la floración. El fotoperiodo induce la floración — el fertilizante la nutre. Cambiar al fertilizante de floración antes de que la planta haya iniciado la señalización hormonal no acelera el proceso; solo cambia el perfil nutricional en un momento en que el perfil vegetativo sigue siendo el más apropiado.',
  'La transición nutricional no es una fecha en el calendario: es una respuesta al estado de la planta. La señal de que el stretch está completando y el perfil puede moverse hacia floración son los primordios florales visibles. Observar la planta durante la transición produce mejores resultados que seguir un cronograma fijo.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  36,
  'Cómo comparar ciclos con datos propios: el historial como herramienta técnica',
  'Variables históricas + comparación sistemática',
  'Análisis comparativo',
  'Usar los registros de ciclos anteriores para comparar resultados de forma estructurada, identificar qué variables cambiaron entre ciclos y qué efectos tuvieron esos cambios.',
  'Error frecuente',
  'Comparar ciclos de memoria. La memoria recuerda los eventos extremos (el ciclo que funcionó muy bien, el que falló) pero comprime o elimina los datos intermedios que explican por qué. La comparación sin registros produce conclusiones sobre diferencias imaginadas.',
  'Qué ocurre realmente',
  'La comparación de ciclos tiene valor diagnóstico solo cuando se comparan variables específicas que se midieron de la misma forma en ambos ciclos. Sin esa condición, la comparación es una narrativa, no un análisis.

Una comparación válida requiere cuatro elementos: el mismo conjunto de variables medidas (pH, EC entrada, EC runoff, temperatura, HR mínima), registradas en las mismas fases del ciclo (semana 1, semana 4, semana 8), con el mismo instrumento o con instrumentos calibrados de forma verificable, y con alguna nota sobre los cambios deliberados entre ciclos (diferente sustrato, diferente agua, diferente fertilizante).

Las diferencias que emergen de esa comparación son información real sobre qué cambió. Las diferencias que no emergen (porque no se registró) son información perdida permanentemente — no se puede reconstruir el pH del ciclo anterior de memoria.

El análisis comparativo no requiere software especializado. Una hoja de cálculo con dos columnas (ciclo anterior y ciclo actual) para cada variable, por semana, produce toda la información necesaria para identificar dónde los ciclos difirieron y en qué período.',
  'Estructura de comparación entre ciclos',
  '["Ciclo anterior: pH semana 3 promedio 6.4, EC runoff 2.1, temperatura 24°C → resultado: floración normal","Ciclo actual: pH semana 3 promedio 6.9, EC runoff 2.8, temperatura 24°C → resultado: clorosis intervenal en semana 4","Diferencia identificada: pH +0.5 unidades y EC runoff +0.7 → correlación con cambio de agua de red en diciembre → carbonatos del agua estacional como causa probable","Acción ciclo siguiente: medir alcalinidad del agua de red en diciembre, considerar cambio a ósmosis en esa época"]'::jsonb,
  'Hipótesis a descartar',
  'Que las diferencias entre ciclos se deben principalmente a la ''suerte'' o a la genética. La variabilidad no controlada entre ciclos casi siempre tiene causas identificables cuando se tienen datos comparables. La genética explica la variabilidad dentro del rango esperado para esa variedad — no las diferencias en pH, EC o síntomas que aparecen y desaparecen entre ciclos.',
  'El historial de datos propio es la única fuente de información perfectamente calibrada para ese cultivador, ese sustrato, ese espacio y esa agua. Ningún manual externo puede reemplazar esa información. Los ciclos sin registro son experimentos cuyos resultados no se pueden reproducir ni analizar.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  37,
  'Identificar errores sistemáticos: cuando el mismo problema aparece en ciclos distintos',
  'Patrón repetido + causa estructural',
  'Detección de patrones',
  'Distinguir los errores que son específicos de un ciclo de los que se repiten de forma sistemática, porque los errores sistemáticos indican una causa estructural que no se resuelve con correcciones puntuales.',
  'Error frecuente',
  'Resolver cada ocurrencia del mismo problema como si fuera un evento nuevo y único. Si el pH sube en semana 3 en el ciclo 1, vuelve a subir en semana 3 en el ciclo 2, y vuelve en semana 3 en el ciclo 3, el problema no es de ese ciclo — es del sistema.',
  'Qué ocurre realmente',
  'Un error sistemático es una falla que se repite en múltiples ciclos bajo las mismas condiciones estructurales (mismo espacio, mismo agua, mismo sustrato, misma época del año). La repetición es la evidencia de que la causa no es un evento aleatorio sino una variable que no se está controlando.

Las causas más comunes de errores sistemáticos en cultivo indoor son:
- Calidad del agua estacional: el agua de red cambia de composición con las estaciones. Un problema que aparece siempre en diciembre-enero puede deberse a cambios en la alcalinidad del agua.
- Temperatura estacional: el espacio se calienta más en verano y se enfría en invierno. Un problema que aparece siempre en julio puede ser temperatura del sustrato baja.
- Agotamiento del sustrato: si se reutiliza el sustrato, se va compactando y reduciendo su capacidad de drenaje ciclo a ciclo. Un problema que empeora progresivamente entre ciclos en el mismo sustrato indica degradación.
- Comportamiento del fertilizante: algunos fertilizantes interactúan con el pH del agua de forma que varía según la dureza del agua. Cambiar de marca sin ajustar el protocolo puede reintroducir un problema resuelto.

Identificar un error como sistemático cambia el tipo de solución: no se trata el evento (el pH de esta semana), se trata la causa estructural (la calidad del agua en esta época).',
  'Identificación de patrón sistemático',
  '["Ciclo 1, semana 4: clorosis intervenal en hojas nuevas → ajustar pH → resuelto","Ciclo 2, semana 4: misma clorosis → ajustar pH → resuelto","Ciclo 3, semana 4: misma clorosis → patrón identificado → ¿qué ocurre siempre en semana 4?","Análisis: pH runoff siempre +0.7 vs entrada en semana 4 → agua de red con alta alcalinidad en ese período → cambio a ósmosis o corrección de alcalinidad → patrón resuelto estructuralmente"]'::jsonb,
  'Hipótesis a descartar',
  'Que si el problema se resuelve en cada ciclo, el sistema está bajo control. Resolver el evento no elimina la causa. Un error que se puede resolver es mejor que uno que no se puede, pero un error que no se repite es mejor que ambos. La diferencia entre gestionar y optimizar es exactamente esta: el cultivador que optimiza no solo resuelve los problemas que aparecen sino que elimina los que se van a repetir.',
  'Tres repeticiones del mismo problema en las mismas condiciones es suficiente para clasificarlo como sistemático. Con esa clasificación, el objetivo cambia de ''arreglarlo esta vez'' a ''identificar y eliminar la causa estructural''. Esa diferencia define qué nivel de dominio técnico tiene el cultivador sobre su propio sistema.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  38,
  'Qué métricas importan según tu objetivo: optimizar lo que produce resultados, no lo que es fácil de medir',
  'Objetivo + variable relevante + prioridad',
  'Priorización avanzada',
  'Identificar cuáles son las variables que tienen mayor impacto sobre el resultado que el cultivador está intentando optimizar, y distinguirlas de las variables que son fáciles de medir pero tienen bajo impacto sobre ese objetivo.',
  'Error frecuente',
  'Optimizar el parámetro que se tiene el instrumento para medir. Si se tiene pHmetro pero no higrómetro calibrado ni termómetro IR, se tiende a atribuir todos los problemas al pH y a invertir tiempo en ajustes de pH que podrían tener menor impacto que un ajuste de VPD que no se está midiendo.',
  'Qué ocurre realmente',
  'Las variables de cultivo no tienen el mismo impacto sobre todos los objetivos. El impacto de cada variable depende del objetivo que se está optimizando.

Si el objetivo es maximizar el rendimiento de peso fresco por vatio de luz, las variables de mayor impacto son la intensidad lumínica (PPFD), la temperatura del canopy y el VPD durante floración. El pH importa, pero su impacto en rendimiento bruto es menor que el de la luz y la temperatura cuando está dentro del rango aceptable.

Si el objetivo es maximizar la concentración de terpenos y compuestos secundarios, las variables de mayor impacto son la diferencia de temperatura día-noche en floración tardía, el estrés controlado por ligera deficiencia hídrica en las últimas semanas, y el VPD específico de la genética. El pH en rango correcto es necesario pero no diferenciador.

Si el objetivo es minimizar la variabilidad entre ciclos, las variables de mayor impacto son la calidad del agua base, la consistencia del protocolo de medición y la temperatura del espacio. El calibrado de los instrumentos es crítico para este objetivo porque la variabilidad en las mediciones se confunde con variabilidad real del sistema.

El ejercicio de identificar métricas relevantes empieza por definir el objetivo con precisión, luego listar las variables que tienen mayor probabilidad de afectarlo, y finalmente verificar cuáles de esas variables están bajo control o medición activa.',
  'Mapeo objetivo → métricas relevantes',
  '["Objetivo: reducir la variabilidad de pH entre ciclos → métricas relevantes: alcalinidad del agua de red, calidad de la calibración del pHmetro, frecuencia de medición del runoff","Objetivo: maximizar terpenos en floración tardía → métricas relevantes: temperatura nocturna mínima (semana 8–12), VPD promedio del período, hidratación en las últimas 2 semanas","Objetivo: reproducir el mejor ciclo → métricas relevantes: todas las variables que fueron diferentes en ese ciclo vs los anteriores — requiere haber registrado ambos"]'::jsonb,
  'Hipótesis a descartar',
  'Que optimizar todo lo que se puede medir es la mejor estrategia. La optimización de variables de bajo impacto consume tiempo y atención que podrían aplicarse a las variables de alto impacto. El cultivador con recursos limitados (tiempo, instrumentos, energía) produce mejores resultados si identifica y optimiza las dos o tres variables de mayor impacto para su objetivo específico.',
  'La pregunta que define el nivel de optimización no es ''¿qué puedo medir?'' sino ''¿qué variable tiene el mayor impacto sobre el resultado que quiero mejorar?'' Responderla con datos propios de ciclos anteriores convierte la optimización en una actividad dirigida, no en un ajuste de parámetros al azar.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  39,
  'Cómo reducir la variabilidad de pH entre ciclos: atacar la causa, no el síntoma',
  'pH + agua base + sustrato + protocolo',
  'Estandarización',
  'Identificar las fuentes de variabilidad de pH entre ciclos y diseñar intervenciones estructurales que reduzcan esa variabilidad, en lugar de corregir el pH cada vez que se desvía.',
  'Error frecuente',
  'Aceptar que el pH ''siempre hay que ajustarlo'' como una constante del cultivo, sin investigar por qué se desvía ni si esa desviación podría reducirse. El pH que se estabiliza solo requiere menos intervención y produce condiciones más consistentes.',
  'Qué ocurre realmente',
  'La variabilidad de pH entre ciclos tiene fuentes identificables. Las más comunes son:

1. Calidad del agua variable. El agua de red cambia su composición a lo largo del año según la época de lluvias, la fuente y el tratamiento. Un agua con alcalinidad de 80 mg/L en verano puede tener 160 mg/L en invierno. Esa diferencia produce un comportamiento de pH completamente distinto con el mismo protocolo de preparación del reservorio.

2. Degradación del sustrato. Un sustrato que se ha usado en múltiples ciclos tiene menor capacidad de intercambio catiónico y menos buffer de pH que uno nuevo. El mismo agua y fertilizante produce un pH más inestable en un sustrato degradado.

3. Temperatura del agua. La temperatura del agua de riego afecta la solubilidad de los carbonatos y la actividad de las bacterias nitrificantes en el sustrato. En invierno con agua a 10°C, el comportamiento del pH es diferente al de verano con agua a 22°C.

4. Inconsistencia en el protocolo de medición. Si el pHmetro no se calibra con la misma regularidad entre ciclos, la deriva del instrumento produce variabilidad aparente que no es variabilidad real del sistema.

Atacar cada una de estas fuentes de variabilidad de forma estructural (cambiar a agua de ósmosis, renovar el sustrato cada ciclo o cada dos ciclos, atemperar el agua en invierno, establecer un calendario fijo de calibración) produce ciclos más predecibles sin necesidad de más correcciones manuales.',
  'Fuentes de variabilidad y sus soluciones estructurales',
  '["Fuente: agua de red variable → solución estructural: agua de ósmosis o medición de alcalinidad mensual","Fuente: sustrato degradado → solución estructural: renovar sustrato cada 1–2 ciclos, registrar la fecha del cambio","Fuente: temperatura del agua variable → solución estructural: atemperar el agua a 20–22°C antes de preparar el reservorio","Fuente: calibración irregular del pHmetro → solución estructural: calibrar cada 7 días, registrar fecha y resultado de la calibración"]'::jsonb,
  'Hipótesis a descartar',
  'Que la variabilidad de pH entre ciclos es normal e inevitable. Cierta variabilidad es normal porque algunas fuentes son difíciles de controlar completamente. Pero la mayor parte de la variabilidad observada en la práctica proviene de fuentes controlables — y la prueba es que cultivadores que abordan esas fuentes de forma estructural obtienen ciclos con variabilidad de pH significativamente menor.',
  'La variabilidad de pH entre ciclos no es aleatoria — tiene causas identificables y reducibles. El cultivador que identifica sus propias fuentes de variabilidad y las aborda de forma estructural deja de gastar tiempo en correcciones repetitivas y empieza a operar un sistema que se estabiliza solo en el rango correcto.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  40,
  'Cómo ajustar el calendario de nutrición a tus datos: del protocolo genérico al protocolo propio',
  'EC + respuesta de la planta + fase',
  'Nutrición personalizada',
  'Adaptar el calendario de nutrición genérico del fabricante de fertilizantes a las condiciones específicas del cultivo propio, usando los datos de respuesta de la planta como criterio de ajuste.',
  'Error frecuente',
  'Seguir el calendario de nutrición del fabricante durante múltiples ciclos sin evaluar si los valores producen la respuesta esperada en ese espacio específico con esa agua y ese sustrato. El calendario del fabricante es un punto de partida, no un protocolo final.',
  'Qué ocurre realmente',
  'Los calendarios de nutrición de los fabricantes se diseñan para condiciones genéricas — agua de calidad estándar, sustrato neutro, temperatura ambiente controlada. Cuando las condiciones reales difieren, el calendario produce resultados diferentes a los esperados.

Los ajustes más comunes que requieren los cultivadores respecto a los calendarios genéricos son:

1. EC base más baja. Los calendarios suelen asumir agua de red con EC 0.0–0.2. Con agua de red con EC 0.4–0.6, la EC real del reservorio es significativamente más alta que la indicada. Si el calendar indica EC 2.0 y el agua ya aporta 0.5, la EC real es 2.5 — a menudo en el límite superior del rango seguro.

2. Timing de transición entre fases. Las semanas del calendario se calculan desde el cambio de fotoperiodo, pero la velocidad de stretch varía según la genética. Una genética que hace stretch durante 3 semanas necesita el calendario de floración tardío; una que lo hace en 1 semana puede avanzar más rápido.

3. Respuesta específica a micro y macronutrientes. Algunas genéticas son más sensibles al nitrógeno (se queman con EC baja) y otras más tolerantes. Los datos de ECrunoff y los síntomas foliares de ciclos anteriores son los indicadores más confiables de cuánto fertilizante tolera esa planta específica en ese espacio.',
  'Proceso de ajuste del calendario',
  '["Ciclo 1 (baseline): seguir el calendario del fabricante, registrar EC entrada, EC runoff y síntomas semana a semana","Ciclo 1 análisis: ¿hubo síntomas de exceso (bordes quemados, EC runoff > 3.0)? → reducir EC objetivo en 10–15%","Ciclo 1 análisis: ¿hubo síntomas de deficiencia con pH correcto y EC en rango? → revisar si la genética requiere más de algún elemento específico","Ciclo 2 (ajustado): aplicar el calendar modificado, verificar si los síntomas de ciclo 1 desaparecieron → iteración convergente hacia el protocolo propio"]'::jsonb,
  'Hipótesis a descartar',
  'Que el calendario del fabricante es conservador y siempre se puede subir la EC con seguridad. Algunos cultivadores asumen que más fertilizante es mejor y elevan la EC por encima del rango indicado sin observar la respuesta de la planta. Los síntomas de exceso (quemaduras, EC runoff alta) tardan en aparecer y cuando lo hacen ya hay daño acumulado.',
  'El protocolo de nutrición propio se construye en dos o tres ciclos con buena observación y registros. Después de ese proceso, el cultivador tiene un calendario adaptado a su agua, su espacio y sus genéticas — más preciso y con menos sorpresas que cualquier guía genérica.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  41,
  'Por qué el VPD óptimo cambia por genotipo: la respuesta estomática como variable individual',
  'VPD + respuesta de genotipo + transpiración',
  'Calibración por genotipo',
  'Comprender que el VPD óptimo no es universal sino que varía según la genética, y que esa variación puede identificarse observando la respuesta estomática y el estado foliar de la planta en distintas condiciones de VPD.',
  'Error frecuente',
  'Aplicar el mismo rango de VPD (0.8–1.2 kPa) a todas las genéticas sin verificar si esa genética específica muestra síntomas de estrés hídrico o subóptima transpiración en ese rango.',
  'Qué ocurre realmente',
  'El VPD óptimo es el rango en que la planta transpira lo suficiente para mantener el flujo de xilema activo (que transporta calcio y otros nutrientes inmóviles) sin generar un déficit hídrico que obligue al cierre estomático.

Este rango no es fijo entre genéticas porque la apertura estomática está controlada por mecanismos que varían entre variedades. Algunos genotipos tienen estomas que responden muy rápido a cambios en el déficit hídrico del aire y los cierran a VPD relativamente bajo (≈0.9 kPa). Otros genotipos mantienen los estomas abiertos hasta VPD más alto (≈1.6 kPa) antes de cerrarlos.

En la práctica, esto significa que una genética con estomas sensibles en un ambiente con VPD 1.4 kPa puede mostrar síntomas de estrés por transpiración excesiva (hojas enrolladas, turgor bajo durante el día) aunque el VPD esté ''en rango''. Otra genética en el mismo ambiente puede estar perfectamente bien.

La forma de identificar el VPD óptimo de una genética específica es observar el estado foliar durante el período de luz a distintos valores de VPD. Las hojas planas, con turgencia visible y sin enrollamiento durante el día indican VPD dentro del rango funcional para esa genética. Las hojas que se enrollan durante el día y se recuperan por la noche indican que el VPD del día está en el límite superior o más allá para esa planta.',
  'Calibración de VPD por genotipo',
  '["Genotipo A en VPD 1.4 kPa: hojas planas durante el día, sin síntomas → VPD 1.4 dentro del rango funcional","Genotipo B en VPD 1.4 kPa: hojas levemente enrolladas durante la tarde, recuperación nocturna → VPD 1.4 en el límite superior","Genotipo B reducido a VPD 1.1 kPa (subir HR de 50% a 58%): hojas planas todo el día → rango funcional para genotipo B: 0.8–1.1 kPa","Registro: en ciclos futuros con genotipo B → objetivo VPD 0.9–1.1 kPa, no el rango genérico 0.8–1.2"]'::jsonb,
  'Hipótesis a descartar',
  'Que el enrollamiento de hojas durante el día es siempre estrés por falta de riego. El enrollamiento diurno con sustrato en condición correcta y recuperación nocturna es el patrón específico del estrés por VPD alto — la planta cierra estomas para reducir la transpiración. Regar más en ese contexto no resuelve el problema y puede crear sobre-riego.',
  'Los rangos genéricos de VPD son el punto de partida. Los datos propios de observación foliar son el calibrador. Una genética de la que se conocen los límites reales de respuesta estomática se cultiva con menor error y mayor consistencia que una que se gestiona con parámetros copiados de una guía.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  42,
  'Cuándo automatizar y cuándo no: la decisión técnica que muchos toman al revés',
  'Consistencia técnica + ROI de la automatización',
  'Decisión técnica de inversión',
  'Evaluar cuándo la automatización de una variable produce resultados mejores que el control manual, y cuándo automatizar introduce complejidad sin beneficio o consolida errores que deberían corregirse primero.',
  'Error frecuente',
  'Automatizar para compensar la falta de consistencia manual. Si el sistema de riego manual produce resultados inconsistentes, la conclusión automática es ''necesito automatización''. Pero si la inconsistencia proviene de una comprensión incompleta del sistema, la automatización solo hace consistente el error.',
  'Qué ocurre realmente',
  'La automatización produce valor bajo dos condiciones: cuando la acción que automatiza es técnicamente correcta y la variabilidad es el problema, y cuando la frecuencia o el timing requieren una consistencia que el control manual no puede mantener.

El control de temperatura y humedad es un candidato natural a la automatización porque la temperatura y la HR cambian de forma continua y la respuesta óptima (ajustar el extractor o el humidificador) requiere una frecuencia de intervención que el control manual no puede sostener de forma consistente durante 24 horas.

El riego automático por tiempo o volumen, sin embargo, puede ser contraproducente si el operador no comprende el ciclo húmedo-seco. Un temporizador que riega cada 12 horas independientemente del estado del sustrato automatiza un criterio incorrecto — el sustrato puede estar saturado o seco en momentos que el timer ignora.

Antes de automatizar una variable, la pregunta técnica es: ¿comprendo suficientemente bien esta variable para que un parámetro fijo (intervalo de tiempo, setpoint de temperatura) produzca el resultado correcto en todas las condiciones que voy a encontrar? Si la respuesta es no, automatizar consolida el desconocimiento en lugar de resolverlo.',
  'Árbol de decisión para automatización',
  '["Variable: temperatura + HR → ¿requiere intervención continua? Sí → ¿el setpoint correcto es identificable? Sí (rangos bien documentados) → automatización produce valor claro","Variable: riego → ¿el timing correcto es consistente? No (depende del estado del sustrato, temperatura, fase del ciclo) → automatización por tiempo/volumen fijo consolida un criterio inadecuado","Variable: riego con sensor de humedad del sustrato calibrado → ¿el sensor mide la variable correcta? Sí → automatización posible si el umbral de activación se calibra correctamente para ese sustrato y fase"]'::jsonb,
  'Hipótesis a descartar',
  'Que la automatización siempre mejora la consistencia. La automatización mejora la consistencia de la acción que se automatiza. Si la acción que se automatiza es incorrecta, la consistencia empeora los resultados. El cultivador que no entiende por qué su riego manual produce buenos resultados no puede automatizar ese riego sin riesgo de degradar los resultados.',
  'La automatización es una herramienta, no un objetivo. Las variables que se benefician más de la automatización son las que requieren intervención frecuente con criterios bien definidos y estables. Las que requieren criterio adaptativo (observación del estado de la planta, ajuste según fase) producen mejor resultado con control informado que con automatización rígida.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  43,
  'Registro digital vs analógico: qué formato produce los datos más útiles para tu forma de trabajar',
  'Formato de datos + accesibilidad + consistencia',
  'Elección de herramienta de registro',
  'Evaluar las ventajas y limitaciones prácticas del registro digital y analógico para decidir cuál produce datos más consistentes y accesibles para la forma específica de trabajar del cultivador.',
  'Error frecuente',
  'Asumir que el registro digital es siempre superior al analógico porque permite gráficos automáticos y búsqueda. El formato óptimo es el que se usa de forma consistente — un cuaderno que se llena cada riego produce datos más valiosos que una app que se abre dos veces en todo el ciclo.',
  'Qué ocurre realmente',
  'El valor del registro no está en el formato sino en la consistencia y la accesibilidad en el momento de necesitar los datos.

El registro analógico (cuaderno, planilla impresa) tiene ventajas en contextos de alta humedad o cuando el cultivador prefiere el proceso de escritura para consolidar la observación. No requiere batería, no falla por actualizaciones de software y está siempre disponible en el espacio de cultivo. Su limitación principal es que los datos no son fácilmente comparables entre ciclos sin transcripción manual o digitalización.

El registro digital (hoja de cálculo, app de cultivo, base de datos simple) permite comparación automática entre ciclos, generación de gráficos de tendencia y búsqueda dentro del historial. Pero requiere que el cultivador lleve el dispositivo al espacio de cultivo en cada medición, tenga batería disponible y el sistema no tenga fricción suficiente para que el registro se postergue.

El indicador de qué formato funciona mejor no es la preferencia teórica sino el comportamiento real: ¿se está registrando de forma consistente con el formato actual? Si hay lagunas frecuentes, el formato tiene fricción que hay que reducir — cambiar a algo más simple, más accesible o más integrado en la rutina de cultivo.',
  'Criterios de selección de formato',
  '["Alta consistencia con cuaderno analógico → mantenerlo; agregar fotografías con fecha como complemento visual no invasivo","Alta consistencia digital pero dificultad para comparar ciclos → estructurar la hoja con columnas por semana y filas por variable → comparación directa entre ciclos sin transcripción","Inconsistencia en cualquier formato → identificar el momento de la rutina donde se pierde el registro → simplificar el formulario a las 5 variables mínimas en ese punto específico","Datos de alta frecuencia (temperatura y HR continua) → logger automático + revisión semanal → no requiere registro manual"]'::jsonb,
  'Hipótesis a descartar',
  'Que el formato del registro afecta la calidad de los datos. El formato afecta la accesibilidad y la facilidad de análisis, pero no la calidad de los datos en sí. Un pH medido con el procedimiento correcto es igualmente válido si se anota en un cuaderno o en una app. Lo que afecta la calidad es el procedimiento de medición y la consistencia del registro, no el soporte donde se guarda.',
  'El mejor sistema de registro es el que se usa. Ese principio simple elimina la discusión sobre cuál es el más sofisticado o el más moderno. Si el formato actual produce lagunas en el registro, hay que simplificarlo hasta que sea consistente — y solo entonces considerar si conviene agregar más estructura o herramientas.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  44,
  'Cómo evaluar si un cambio funcionó realmente: el experimento mínimo válido',
  'Variable experimental + variable de control + resultado medido',
  'Razonamiento experimental básico',
  'Diseñar y ejecutar un cambio de una sola variable de forma que sea posible determinar si ese cambio fue responsable del resultado observado, y distinguirlo de coincidencias o efectos de otras variables.',
  'Error frecuente',
  'Cambiar múltiples variables al mismo tiempo (sustrato, fertilizante y frecuencia de riego) y concluir que ''el cambio funcionó'' o ''no funcionó'' sin poder identificar cuál de los cambios produjo qué efecto.',
  'Qué ocurre realmente',
  'Un cambio solo puede evaluarse como causante de un resultado cuando todas las demás variables permanecen constantes. Esa es la condición del experimento controlado en su forma más básica.

En la práctica del cultivo indoor, mantener todas las variables constantes excepto una requiere planificación deliberada. No es posible cambiar el sustrato y la frecuencia de riego al mismo tiempo y luego determinar cuál de los dos cambios fue responsable de la mejora en el pH del runoff.

El experimento mínimo válido en cultivo tiene tres elementos:
1. Una sola variable que cambia entre el ciclo de control (o el período de control) y el ciclo de prueba.
2. Una medición del resultado de interés antes y después del cambio, usando el mismo instrumento y el mismo procedimiento.
3. Suficiente tiempo para que el efecto del cambio sea observable — al menos dos semanas en la mayoría de las variables de cultivo.

Las comparaciones más confiables son entre dos mitades del mismo espacio (un grupo de plantas con el cambio, otro sin él) o entre dos ciclos consecutivos con solo una variable diferente. Las comparaciones entre ciclos con múltiples variables cambiadas son informativas pero no concluyentes.',
  'Diseño de experimento mínimo',
  '["Variable a evaluar: efecto del agua de ósmosis vs agua de red en la estabilidad del pH","Control: ciclo actual con agua de red → registrar pH entrada, pH runoff, tendencia de pH por semana","Prueba: ciclo siguiente con agua de ósmosis, todo lo demás igual → mismas mediciones, mismo cronograma","Evaluación: ¿la tendencia de pH en semanas 2–4 es diferente entre ciclos? → si sí, con alta probabilidad el cambio de agua fue responsable","Confundidores a controlar: mismo fertilizante, mismo sustrato (nuevo en ambos ciclos), misma época del año si es posible"]'::jsonb,
  'Hipótesis a descartar',
  'Que dos ciclos con el mismo resultado confirman que el cambio funcionó. Un resultado positivo en dos ciclos aumenta la confianza en la hipótesis, pero no la confirma — puede ser coincidencia o efecto de otra variable que también cambió. La confirmación requiere al menos tres ciclos con resultados consistentes y la exclusión activa de explicaciones alternativas.',
  'El experimento mínimo válido no es una operación científica compleja — es una decisión de cambiar solo una cosa a la vez y medir el resultado de forma consistente. Esa disciplina produce conclusiones que pueden usarse en el ciclo siguiente. La ausencia de esa disciplina produce anécdotas que no se pueden reproducir.'
);

INSERT INTO topic_content (topic_id, title, variable, skill, objective, error_label, error_text, mechanism_label, mechanism_text, chain_label, chain_items, discard_label, discard_text, closing) VALUES (
  45,
  'Cuándo un resultado bueno es reproducible: la diferencia entre suerte y control',
  'Condiciones de éxito + variables estables + criterio de repetición',
  'Pensamiento de reproducibilidad',
  'Evaluar si un resultado positivo en un ciclo puede reproducirse en el siguiente, identificando cuáles de las condiciones que lo produjeron son controlables y cuáles fueron variables que cambiaron por razones externas.',
  'Error frecuente',
  'Intentar repetir exactamente lo que se hizo en el ciclo anterior (''sin cambiar nada'') sin verificar si las condiciones del ciclo anterior son idénticas. El agua de red en distintas estaciones, el sustrato nuevo vs el del ciclo anterior, la temperatura del espacio en distinta época — todas estas variables cambian aunque el cultivador no haga nada diferente.',
  'Qué ocurre realmente',
  'Un resultado es reproducible cuando se pueden identificar las variables que lo produjeron y esas variables están bajo control activo.

Un resultado es irrepetible cuando provino de condiciones que no se controlaron ni midieron, o que cambian entre ciclos por razones externas (estacionalidad, calidad del agua, envejecimiento del sustrato).

El proceso de evaluar la reproducibilidad de un resultado tiene dos etapas:

Primera etapa — Atribuir el resultado. ¿Qué variables estuvieron en un rango diferente a los ciclos anteriores? ¿Coincidió el resultado positivo con algún cambio deliberado o con alguna condición inusual? Si no se tienen datos de las variables clave, la atribución es imposible y el resultado es anécdota.

Segunda etapa — Evaluar el control. De las variables que parecen haber contribuido al resultado positivo, ¿cuáles están bajo control activo del cultivador? ¿Cuáles dependen de factores externos? Las variables controlables pueden reproducirse deliberadamente. Las no controlables producen variabilidad que el cultivador no puede reducir sin cambiar algo en el setup.

El resultado más valioso de un buen ciclo no es el resultado en sí — es entender qué lo produjo. Con esa comprensión, el siguiente ciclo es más probable que sea igual de bueno.',
  'Evaluación de reproducibilidad',
  '["Ciclo excepcional: pH ultra-estable + mínimos síntomas + alto rendimiento","Análisis: ese ciclo se hizo en marzo con agua de ósmosis. Los ciclos anteriores usaban agua de red","Variables controladas: agua de ósmosis (deliberado), mismo sustrato nuevo, misma genética","Variable que pudo haber influido: temperatura de marzo (18–22°C) vs julio (28–33°C) — no controlada","Reproducibilidad: alta para los elementos controlados (agua de ósmosis + sustrato nuevo). Baja para la temperatura → en julio hacer misma prueba con clima artificial más activo","Conclusión: el agua de ósmosis es reproducible y se incorpora al protocolo estándar. El resultado de temperatura óptima de marzo no es reproducible sin invertir en control climático"]'::jsonb,
  'Hipótesis a descartar',
  'Que repetir exactamente el mismo procedimiento produce el mismo resultado. El procedimiento es solo una parte de las condiciones. Si el agua cambia, el sustrato envejece o la temperatura del espacio varía entre ciclos, el mismo procedimiento produce resultados diferentes. La reproducibilidad requiere controlar las variables relevantes, no solo repetir los pasos.',
  'La diferencia entre el cultivador que mejora consistentemente y el que tiene buenos y malos ciclos sin patrón claro es esta: el primero sabe qué produjo sus buenos ciclos y puede reproducirlo. El segundo repite los mismos pasos esperando el mismo resultado aunque las condiciones cambien. Los datos propios, acumulados con consistencia, son la única herramienta que produce esa comprensión.'
);

