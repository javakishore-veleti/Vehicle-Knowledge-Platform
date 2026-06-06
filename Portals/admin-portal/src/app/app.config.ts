import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { definePreset } from '@primeng/themes';

import { routes } from './app.routes';
import { authInterceptor } from './core/auth.interceptor';

// VKP brand: violet primary (ties PrimeNG buttons/menus/tables to the portal's violet+rose palette).
const VkpAura = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#f3eefe', 100: '#e4d4ff', 200: '#cdb2ff', 300: '#b388ff', 400: '#a855f7',
      500: '#7c3aed', 600: '#6d28d9', 700: '#5b21b6', 800: '#4c1d95', 900: '#3b0d77', 950: '#2a0a57'
    }
  }
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withFetch(), withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
    // Light theme by default; dark would require the `.app-dark` class (never added here).
    providePrimeNG({ theme: { preset: VkpAura, options: { darkModeSelector: '.app-dark' } } })
  ]
};
