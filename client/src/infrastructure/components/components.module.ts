import { NgModule } from '@angular/core';
import { StepperComponent } from './stepper.component';
import { BrowserModule } from '@angular/platform-browser';
import { IonicPageModule } from 'ionic-angular';
import { PageComponent } from './page.component';

@NgModule({
    declarations: [
        PageComponent,
        StepperComponent
    ],
    imports: [
        BrowserModule,
        IonicPageModule.forChild(StepperComponent)
    ],
    entryComponents: [
        PageComponent,
        StepperComponent
    ],
    providers: [],
    exports: [
        PageComponent,
        StepperComponent
    ]
})
export class HeartstepsComponentsModule {}
