"""Plot observed wrong switches and explicit abstentions as separate, overlapping events."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    """Create a descriptive figure without treating abstentions as correct or wrong answers."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', required=True)
    args = parser.parse_args()
    folder = Path(args.experiment)
    data = json.loads((folder/'analysis.json').read_text())
    datasets = [('truthfulqa_binary','TruthfulQA adaptation'),('mmlu_5subjects','MMLU: five subjects'),
                ('synthetic_evidence','Synthetic records')]
    conditions = ['control','disagreement','weak_argument']
    fig, axes = plt.subplots(1,3,figsize=(12,5),sharey=True)
    for ax,(key,title) in zip(axes,datasets):
        for index,kind in enumerate(conditions):
            stats = data['main'].get(key+'/'+kind)
            if not stats or not stats['n']:
                continue
            for offset,field,color,label in [(-.18,'observed_wrong_switches','#d47745','Any wrong switch'),
                                              (.18,'incomplete_conversations','#8794a3','Any abstention')]:
                value = stats[field]/stats['n']*100
                ax.bar(index+offset,value,color=color,width=.34,label=label if index==0 else None)
                ax.text(index+offset,value+2,f"{stats[field]}/{stats['n']}",ha='center',fontsize=8)
        ax.set_title(title,fontsize=11)
        ax.set_xticks(range(3),['Neutral','Disagree','Weak\nargument'])
        ax.set_ylim(0,120)
        ax.set_yticks([0,25,50,75,100])
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Eligible conversations (%)')
    axes[0].legend(loc='upper left',fontsize=8,frameon=False)
    fig.suptitle('Qwen2.5-3B: exploratory short-context results',fontsize=15)
    fig.text(.5,.015,'Five rounds per conversation. Wrong switches and abstentions can occur in the same conversation.\nDescriptive counts only; small selected samples, not official benchmark scores. Abstention is not a correct answer.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.1,1,.93))
    fig.savefig(folder/'main_results.png',dpi=160)


if __name__ == '__main__':
    main()
