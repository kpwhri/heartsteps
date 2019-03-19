import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { ContactInformationService } from '@heartsteps/contact-information/contact-information.service';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';
import { FormModule } from '@infrastructure/form/form.module';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        FormModule,
        IonicPageModule.forChild(ParticipantInformation),
    ],
    providers: [
        ContactInformationService
    ],
    declarations: [
        ParticipantInformation
    ],
    exports: [
        ParticipantInformation
    ]
})
export class ContactInformationModule {}
