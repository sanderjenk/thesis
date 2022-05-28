import { Component, OnInit } from '@angular/core';
import { IssuesService } from '../issues.service';
import { Issue } from '../issue';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChartConfiguration, ChartData, ChartEvent, ChartType } from 'chart.js';

@Component({
  selector: 'app-selected-issues',
  templateUrl: './selected-issues.component.html',
  styleUrls: ['./selected-issues.component.css'],
})
export class SelectedIssuesComponent implements OnInit {
  generatedIssues: Issue[] = [];
  showSpinner = false;
  feedbackForm: any;
  generateForm: any;
  developers: string[] = []
  velocity: number = 0;
  ffs: number[] = []

  public radarChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    scales: {
      r: {
          angleLines: {
              display: false
          },
          suggestedMin: 0,
          suggestedMax: 3
      },
    }
  };

  radarChartLabels: string[] = [ 'Business value', 'Experience', 'Novelty'];

  radarChartData: ChartData<'radar'> = {
    labels: this.radarChartLabels,
    datasets: [
      { data: [], label: 'Objective values of the solution' }
    ]
  };
  radarChartType: ChartType = 'radar';


  constructor(private issuesService: IssuesService, private _snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.getGeneratedIssues();
    this.initGenerateForm();
    this.getDevelopers();
  }

  changeRadarChartData() {
    this.radarChartData.datasets = [
        { data: this.ffs, label: 'Objective values of the solution' }
      ];
  }

  changeRadarChartOptions(velocity: number) {
    this.radarChartOptions = {
      responsive: true,
      scales: {
        r: {
            angleLines: {
                display: false
            },
            suggestedMin: 0,
            suggestedMax: velocity
        },
      }
    };
  }
  
  initGenerateForm() {
    this.generateForm = new FormGroup({
      storypoints: new FormControl(null, [Validators.required]),
      developer: new FormControl(null, Validators.required)
    });
  }

  getDevelopers() {
    this.issuesService.getDevelopers().subscribe((developers: string[]) => {
      this.developers = developers;
    })
  }
  
  getGeneratedIssues() {
    this.issuesService.generatedIssuesSubject.subscribe((issues: Issue[]) => {
      this.generatedIssues = issues;
    })
  }

  generate() {
    this.showSpinner = true;
    this.issuesService.generatedIssuesSubject.next([]);
    this.changeRadarChartOptions(this.generateForm.value.storypoints)
    this.issuesService.generateReccommendations(this.generateForm.value.storypoints, this.generateForm.value.developer).subscribe((res: any) => {
      let issues = JSON.parse(res.items);
      let ffs = JSON.parse(res.ffs);
      this.ffs = ffs.map((x: number)=> x * -1)
      this.changeRadarChartData();
      this.issuesService.generatedIssuesSubject.next(issues);
      this.showSpinner = false;
    });
  }

  getVelocity() {
    this.issuesService.getVelocity(this.generateForm.value.developer).subscribe(velocity => {
      this.velocity = velocity;
      this.generateForm.controls.storypoints.setValue(velocity);
    })
  }
}
