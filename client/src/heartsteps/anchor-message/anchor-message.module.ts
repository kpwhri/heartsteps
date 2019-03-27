import { NgModule } from "@angular/core";
import { AnchorMessageComponent } from "./anchor-message.component";
import { BrowserModule } from "@angular/platform-browser";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { AnchorMessageService } from "./anchor-message.service";



@NgModule({
    declarations: [
        AnchorMessageComponent
    ],
    exports: [
        AnchorMessageComponent
    ],
    imports: [
        BrowserModule,
        InfrastructureModule
    ],
    providers: [
        AnchorMessageService
    ]
})
export class AnchorMessageModule {}
