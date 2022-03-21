import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IntroComponent } from './intro/intro.component';
import { ProjectGuard } from './project.guard';
import { ProjectsComponent } from './projects/projects.component';
import { SelectedIssuesComponent } from './selected-issues/selected-issues.component';

const routes: Routes = [
  { 
    path: '', 
    component: IntroComponent 
  },
  { 
    path: 'generate', 
    component: SelectedIssuesComponent, 
    canActivate: [ProjectGuard]
},
  { 
    path: 'projects', 
    component: ProjectsComponent 
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
