import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { LocationPermission } from './location-permission';
import { LocationService } from '@infrastructure/location.service';


@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(LocationPermission),
    ],
    providers: [
        LocationService
    ],
    declarations: [
        LocationPermission
    ],
    exports: [
        LocationPermission
    ]
})
export class LocationModule {}
