import { NgModule } from '@angular/core';
import { MorningMessageService } from './morning-message.service';
import { AnchorMessageComponent } from './anchor-message.component';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    imports: [
        BrowserModule
    ],
    providers: [
        MorningMessageService
    ],
    declarations: [
        AnchorMessageComponent
    ],
    exports: [
        AnchorMessageComponent
    ]
})
export class MorningMessageModule {}
