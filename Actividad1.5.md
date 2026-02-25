# 1.5 Herramientas de IA cotidianas

1. **Claude**: Se ha posicionado como uno de los modelos de lenguaje más avanzados para tareas de razonamiento complejo y redacción de código. Su ventana de contexto extendida permite analizar documentos extensos de una sola vez.

https://privacy.claude.com/es/articles/7996885-como-utiliza-datos-personales-en-el-entrenamiento-de-modelos
https://privacy.claude.com/es/articles/10301952-actualizaciones-de-nuestra-politica-de-privacidad

2. **Midjourney**: 
Es actualmente la referencia en generación de imágenes artísticas mediante IA generativa. Funciona principalmente a través de Discord y destaca por su estética fotorrealista y artística superior.

https://docs.midjourney.com/hc/en-us/articles/32083055291277-Terms-of-Service

3. **ElevenLabs**:
Líder en la síntesis de voz (Text-to-Speech) y clonación de audio. Utiliza modelos de aprendizaje profundo para generar locuciones con una entonación y emoción extremadamente realistas en múltiples idiomas.

https://elevenlabs.io/es/dpa
https://elevenlabs.io/es/privacy-policy

4. **Perplexity AI**:
Es un motor de búsqueda conversacional que combina modelos de lenguaje con acceso a internet en tiempo real para ofrecer respuestas citando fuentes directas.

https://www.perplexity.ai/es/hub/legal/dpa
https://www.perplexity.ai/es/hub/legal/privacy-policy

5. **GitHub Copilot**
Una herramienta esencial para el desarrollo de software que actúa como un programador de par (pair programmer). Se integra directamente en editores como VS Code para sugerir líneas de código o funciones completas en tiempo real.

https://github.com/features/copilot?locale=es-419

---
1. Claude (Anthropic) - Riesgo: Bajo (Uso Corporativo) / Medio (Uso Gratuito)
Privacidad y Entrenamiento: Anthropic es una de las empresas más transparentes. Sus políticas distinguen claramente entre usuarios de pago y gratuitos.

Cuentas Enterprise/API: No utilizan tus datos para entrenar sus modelos de forma predeterminada.

Cuentas Gratuitas/Pro: Pueden utilizar los datos para mejorar sus modelos, aunque permiten el opt-out (darse de baja de esta función).

Riesgo Principal: Fugas accidentales de información sensible en el prompt si no se utiliza la versión Enterprise. Su enfoque en "IA Constitucional" reduce el riesgo de generar respuestas tóxicas o que violen la privacidad de terceros.

2. GitHub Copilot (Microsoft/GitHub) - Riesgo: Bajo (Uso Corporativo) / Medio (Uso Individual)
Privacidad y Entrenamiento:

Copilot for Business/Enterprise: GitHub garantiza que los fragmentos de código del usuario no se conservan ni se utilizan para entrenar el modelo base.

Copilot Individual: Puede utilizar fragmentos de tu código para mejorar las sugerencias, a menos que lo desactives manualmente en la configuración.

Riesgo Principal: Propiedad Intelectual. Existe un riesgo residual de que la herramienta sugiera código que se parezca a bibliotecas con licencias restrictivas (aunque tienen filtros para evitarlo). Para empresas, el riesgo es bajo por sus fuertes cláusulas de indemnización legal.

3. Perplexity AI - Riesgo: Medio
Privacidad y Entrenamiento: Actúa como un motor de búsqueda. Recopila consultas y, en sus versiones gratuitas, utiliza las interacciones para mejorar su algoritmo conversacional.

Manejo de Datos: Al ser un buscador, los datos de navegación y consultas suelen ser compartidos con proveedores de modelos (como OpenAI o Anthropic) y socios de búsqueda (como Bing), aunque de forma anonimizada.

Riesgo Principal: Exposición de consultas. Al usarlo para investigar datos internos o privados de una empresa, esa información queda en sus registros de historial y entrenamiento, a menos que se use la versión Pro con la configuración de privacidad activada.

4. Midjourney - Riesgo: Medio - Alto
Privacidad y Entrenamiento: Por defecto, Midjourney es una herramienta pública. Todo lo que generas en sus canales de Discord es visible para otros usuarios.

Manejo de Datos: Solo los planes de mayor costo (Pro/Mega) ofrecen el "Modo Stealth" (Sigilo) para que tus creaciones y prompts sean privados.

Riesgo Principal: Privacidad y Derechos de Autor. Si generas imágenes con nombres de personas reales o conceptos confidenciales, otros usuarios pueden verlos. Además, los términos de servicio otorgan a Midjourney una licencia perpetua para usar tus creaciones.

5. ElevenLabs - Riesgo: Alto
Privacidad y Entrenamiento: Procesan datos biométricos (muestras de voz). Su política indica que retienen los datos de voz para generar modelos y pueden usarlos para mejorar sus servicios de investigación y seguridad.

Manejo de Datos: Requieren verificar la identidad para la clonación de voces profesionales para evitar Deepfakes, pero la base de datos de "huellas de voz" es información extremadamente sensible.

Riesgo Principal: Seguridad Biométrica. El compromiso de una cuenta podría exponer tu identidad vocal, la cual puede ser utilizada para suplantación de identidad en otros servicios (como banca telefónica). Es la herramienta con los datos más "personales" de la lista.
