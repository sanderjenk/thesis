import pandas as pd
import helpers.lda as lda
import helpers.other_helpers as h
from ast import literal_eval
import glob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
pd.options.mode.chained_assignment = None  # default='warn'

def plot_number_of_topics_hypervolume():
	params_df = pd.read_csv('./thesis-api/algorithm/lda_tuning_results/lda_params.csv', encoding='utf-8')

	params_df = params_df.loc[params_df["project"] != "mdl"]
	hv_df = pd.read_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv', encoding='utf-8')
 
	plt.figure(figsize=(7, 5))
	plt.scatter(params_df["topics"], hv_df["Weighted Avg"],  facecolor="red", edgecolor='black', marker="o")
	for i, label in enumerate(hv_df["project"].tolist()):
		plt.annotate(label.upper(), (params_df["topics"].tolist()[i], hv_df["Weighted Avg"].tolist()[i]))
	plt.title("Number of topics in relation to hypervolume")
	plt.xlabel("Topics")
	plt.ylabel("Hypervolume")
	plt.savefig('./thesis-api/algorithm/validation/plots2/topics_hypervolume_plot.png')
 
def barchart():
	hv_df = pd.read_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv', encoding='utf-8')
	plt.figure(figsize=(7, 5))
	plt.bar(hv_df["project"].str.upper(), hv_df["Weighted Avg"])
	plt.xticks(rotation=90)
	plt.ylabel("Weighted average of hypervolume")
	plt.title("Weighted average hypervolume of projects")
	plt.gcf().subplots_adjust(bottom=0.18)

	plt.savefig('./thesis-api/algorithm/validation/plots2/bar_hypervolume.png')
 
def plot_performance_velocity():
	projects = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')
	
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]

	df = pd.concat(df_list, axis=0)
 
	projects.set_index('project', inplace=True)
 
	test = projects["mean_opt_s"].to_dict()
 
	df["mean_opt_s"] = df["project"].map(test)
 
	df["y"] = (df["opt_execution_time"] / df["mean_opt_s"]) * 100
   	
	plt.scatter(df["velocity"], df["y"],  facecolor="red", edgecolor='black', marker=".")
	plt.xlabel("Velocity")
	plt.ylabel("Dev. opt. time percentage from project mean")
	plt.savefig('./thesis-api/algorithm/validation/plots2/scatter_opt_velocity.png')
 
 
def plot_hv_velocity():
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]

	df = pd.concat(df_list, axis=0)

	df["y"] = (df["hypervolume"] / df["velocity"])

	plt.scatter(df["velocity"], df["y"],  facecolor="red", edgecolor='black', marker=".")
	plt.xlabel("Number of issues")
	plt.ylabel("Per issue HV")
	plt.savefig('./thesis-api/algorithm/validation/plots2/scatter_hv_velocity.png')
 
def plot_opt_velocity_box():
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	df = pd.concat(df_list, axis=0)
 
	ax = df.boxplot(column="opt_execution_time", by="velocity")
	ax.set_title("")
	fig = ax.get_figure()
	fig.suptitle('')
	plt.xlabel("Number of issues")
	plt.ylabel("Optimization time")
	plt.savefig('./thesis-api/algorithm/validation/plots2/box_opt_velocity.png')	
	plt.show()
 
 
def plot_performance_lda():
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	plt.figure(figsize=(7, 5))
 
	donelist = df["done"].tolist()
 
	ldalist = df["lda_s"].tolist()
 
	plt.scatter(df["done"], df["lda_s"],  facecolor="red", edgecolor='black', marker="o")
 
	for i, label in enumerate(df["project"].tolist()):
		plt.annotate(label.upper(), (donelist[i], ldalist[i]))
  
	plt.xlabel("Number of done issues")
	plt.ylabel("LDA training time in seconds")
	plt.savefig('./thesis-api/algorithm/validation/plots2/scatter_lda_done.png')
 
def plot_performance_opt():
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	plt.figure(figsize=(7, 5))
 
	backloglist = df["backlog"].tolist()
 
	optlist = df["mean_opt_s"].tolist()
 
	plt.scatter(df["backlog"], df["mean_opt_s"],  facecolor="red", edgecolor='black', marker="o")
 
	for i, label in enumerate(df["project"].tolist()):
		plt.annotate(label.upper(), (backloglist[i], optlist[i]))
  
	plt.xlabel("Number of backlog issues")
	plt.ylabel("Optimization time in seconds")
	plt.savefig('./thesis-api/algorithm/validation/plots2/scatter_opt_backlog.png')
 
def plot_hv_backlog():
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv', encoding='utf-8')
	df2 = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	plt.figure(figsize=(7, 5))
 
	backloglist = df2["backlog"].tolist()
 
	hv = df["Weighted Avg"].tolist()
 
	plt.scatter(df2["backlog"], df["Weighted Avg"],  facecolor="red", edgecolor='black', marker="o")
 
	for i, label in enumerate(df["project"].tolist()):
		plt.annotate(label.upper(), (backloglist[i], hv[i]))
  
	plt.xlabel("Number of backlog issues")
	plt.ylabel("Optimization time in seconds")
	plt.savefig('./thesis-api/algorithm/validation/plots2/scatter_hv_backlog.png')
 
def generate_word_clouds():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		if (project not in ["xd"]):
			continue

		done = h.get_done_issues(project_df)

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, _ = lda.get_lda_model(done, number_of_topics, alpha, beta)

		for t in range(lda_model.num_topics):
			plt.figure(figsize=(8,3))
			plt.imshow(WordCloud(width = 800, height= 300, background_color= "white").fit_words(dict(lda_model.show_topic(t, 200))))
			plt.axis("off")
			plt.title("Topic #" + str(t+1))
			plt.savefig('./thesis-api/algorithm/validation/plots2/wordcloud_' + project + str(t+1) +  '.png')
   
if __name__ == '__main__':
	# plot_number_of_topics_hypervolume()
	# barchart()
	generate_word_clouds()
	# plot_performance_lda()
	# plot_performance_opt()
	# plot_performance_velocity()
	# plot_hv_backlog()
	# plot_hv_velocity()
	# plot_opt_velocity_box()
	pass