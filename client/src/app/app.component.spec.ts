import {
    async,
    ComponentFixture,
    TestBed
} from '@angular/core/testing';
import { MyApp } from './app.component';
import { IonicModule } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { AuthorizationService } from '@app/authorization.service';
import { BackgroundService } from '@app/background.service.ts';
import { NotificationService } from '@app/notification.service.ts';
import { RouterModule, Router } from '@angular/router';
import { HomePageModule } from '@pages/home/home.module';

class ParticipantServiceMock {

}

class AuthorizationServiceMock {

}

class BackgroundServiceMock {

}

describe('MyApp', () => {
    let component: MyApp;
    let fixture: ComponentFixture<MyApp>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [MyApp],
            imports: [
                RouterModule.forRoot([]),
                HomePageModule,
                IonicModule.forRoot(MyApp)
            ],
            providers: [
                StatusBar,
                SplashScreen,
                { provide: Router, useClass: BackgroundServiceMock },
                { provide: ParticipantService, useClass: ParticipantServiceMock },
                { provide: AuthorizationService, useClass: AuthorizationServiceMock },
                { provide: BackgroundService, useClass: BackgroundServiceMock },
                { provide: NotificationService, useClass: BackgroundServiceMock }
            ]
        });
        fixture = TestBed.createComponent(MyApp);
        component = fixture.componentInstance;
    }))

    test('should exist', () => {
        expect(component).toBeDefined();
    })
});