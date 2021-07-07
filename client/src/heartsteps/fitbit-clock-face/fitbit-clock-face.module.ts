
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { FormModule } from '@infrastructure/form/form.module';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { FitbitClockFacePairComponent } from './fitbit-clock-face-pair.component';
import { FitbitClockFaceService } from './fitbit-clock-face.service';

@NgModule({
    declarations: [
        FitbitClockFacePairComponent
    ],
    entryComponents: [
        FitbitClockFacePairComponent
    ],
    exports: [
        FitbitClockFacePairComponent
    ],
    imports: [
        BrowserModule,
        FormModule,
        InfrastructureModule,
        ReactiveFormsModule
    ],
    providers: [
        FitbitClockFaceService
    ]
})
export class FitbitClockFaceModule {}
