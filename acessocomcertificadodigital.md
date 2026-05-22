Para fazer acesso a sites que exigem cerificado digital deve adicionar nas browser options do playwright:
```python
class PlaywrightBrowserOptions:
    # ... o código anterior permanece o mesmo ...

    def launch(self, playwright):
        headless = self.docker_running
        user_profile = os.environ.get("USERPROFILE")
        user_data_dir = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data Playwright")
        
        # 1. Mapeia o seu certificado A1
        certificados = [{
            "origin": "https://servicos.receitafederal.gov.br", # URL exata onde o certificado será exigido
            "pfxPath": r"C:\caminho\para\seu\certificado.pfx",  # Caminho do arquivo
            "passphrase": "sua_senha_aqui"                      # Senha do certificado
        }]

        # 2. Injeta na criação do contexto
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=headless,
            slow_mo=100,
            client_certificates=certificados, # <--- A MAGIA ACONTECE AQUI
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            viewport={"width": 1280, "height": 728}
        )
        
        from playwright_stealth import Stealth
        Stealth().apply_stealth_sync(context)

        return context.browser, context
```