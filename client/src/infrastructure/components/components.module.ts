import { NgModule } from '@angular/core';
import { StepperComponent } from './stepper.component';
import { BrowserModule } from '@angular/platform-browser';
import { IonicPageModule } from 'ionic-angular';

@NgModule({
    declarations: [
        StepperComponent
    ],
    imports: [
        BrowserModule,
        IonicPageModule.forChild(StepperComponent)
    ],
    entryComponents: [
        StepperComponent
    ],
    providers: [],
    exports: [
        StepperComponent
    ]
})
export class HeartstepsComponentsModule {}
