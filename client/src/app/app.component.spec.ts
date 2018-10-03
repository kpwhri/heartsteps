import {
    async,
    ComponentFixture,
    TestBed
} from '@angular/core/testing';
import { MyApp } from './app.component';
import { IonicModule } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participant.service';
import { AuthorizationService } from '@infrastructure/authorization.service';

class ParticipantServiceMock {

}

class AuthorizationServiceMock {

}

describe('MyApp', () => {
    let component: MyApp;
    let fixture: ComponentFixture<MyApp>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [MyApp],
            imports: [IonicModule.forRoot(MyApp)],
            providers: [
                StatusBar,
                SplashScreen,
                { provide: ParticipantService, useClass: ParticipantServiceMock },
                { provide: AuthorizationService, useClass: AuthorizationServiceMock }
            ]
        });
        fixture = TestBed.createComponent(MyApp);
        component = fixture.componentInstance;
    }))

    test('should exist', () => {
        expect(component).toBeDefined();
    })
});