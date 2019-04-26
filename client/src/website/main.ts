import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app.module';

console.log('Hi im a website')

platformBrowserDynamic().bootstrapModule(AppModule);
