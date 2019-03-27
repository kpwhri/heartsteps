import { NgModule } from '@angular/core';
import { MorningMessageService } from './morning-message.service';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    imports: [
        BrowserModule
    ],
    providers: [
        MorningMessageService
    ]
})
export class MorningMessageModule {}
