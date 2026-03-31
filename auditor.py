import asyncio
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
from PIL import Image
import base64

# Configuración
client = genai.Client(api_key="AIzaSyAW69q-nhWiDqKFl0uSA40WHFZBhB0zNmw")

async def auditar_sitio(url):
    async with async_playwright() as p:
        # 1. Navegación
        print(f"Abriendo {url}...")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(4000)

        # 2. Captura de datos
        screenshot_path = "audit_screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        html_content = await page.content()
        await browser.close()

        # 3. Leer imagen y convertir a base64
        with open(screenshot_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # 4. El Prompt del Experto
        prompt = f"""
Actúa como un Consultor Senior de SEO y Accesibilidad (WCAG).
Analiza esta captura de pantalla y el código HTML adjunto para el sitio: {url}

TAREAS:
1. SEO: ¿Hay una jerarquía clara de etiquetas H1, H2?
2. Accesibilidad: ¿Los botones tienen etiquetas descriptivas (aria-labels)?
3. Visual: ¿Hay elementos que se cortan o no cargan bien?
4. Código: Revisa este fragmento del DOM y busca errores: {html_content[:5000]}

Responde con un formato de 'Hallazgo' y 'Sugerencia técnica'.
"""

        print("Analizando con Gemini...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=image_data, mime_type="image/png")
            ]
        )

        print("\n--- INFORME DE AUDITORÍA ---")
        print(response.text)

# Ejecuta el auditor
asyncio.run(auditar_sitio("https://www.heb.com.mx/"))