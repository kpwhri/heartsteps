import { NgModule } from '@angular/core';
import { HeartstepsStepperComponent } from './stepper.component';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    declarations: [
        HeartstepsStepperComponent
    ],
    imports: [
        BrowserModule
    ],
    entryComponents: [
        HeartstepsStepperComponent
    ],
    providers: [],
    exports: [
        HeartstepsStepperComponent
    ]
})
export class HeartstepsComponentsModule {}
