import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

// Browser bootstrap is intentionally thin; runtime behavior lives in Angular modules.
platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));
