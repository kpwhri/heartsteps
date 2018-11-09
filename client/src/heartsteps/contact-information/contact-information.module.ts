import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { ContactInformationService } from '@heartsteps/contact-information/contact-information.service';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
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
