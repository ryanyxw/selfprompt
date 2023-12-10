
#a generator that yields each row in a dataset while performing some processing
def dataset_generator(dataset, prefix):
    #we use the typical formatting for demonstrations, except we don't have a gold label
    from selfinstruct.demonstrations.formatting import template_demonstration_formatting
    for i in range(len(dataset)):
        yield (prefix + template_demonstration_formatting(dataset[i]["premise"], dataset[i]["hypothesis"], "")), dataset[i]["gold_label"]


def import_demonstration(txt_file_path):
    with open(txt_file_path, 'r') as f:
        return f.read()


def send_query_to_openai(query_input):
    # import pdb
    # pdb.set_trace()
    from openai import OpenAI

    client = OpenAI()

    response = client.completions.create(
        model="text-davinci-003",
        prompt=query_input,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        return response.choices[0].text
    except:
        return ""
def query_openai(args):
    import json
    import os
    from tqdm import tqdm
    # import the openAI API key
    from dotenv import load_dotenv
    load_dotenv('/home/ryan/selfprompt/.env')
    #we first load the demonstrations that we want to always append
    demonstrations = import_demonstration(args.demonstration_file)

    #get the dataset that we will perform inference on
    from selfinstruct.evaluations.utils import setup_dataset_evaluation
    dataset = setup_dataset_evaluation(args.num_evaluations, args.seed)

    #start writing to the output file, overwriting previous if necessary
    with open(os.path.join(args.out, args.exp_name + ".jsonl"), 'w') as f:
        #loop through the dataset with a generator, which will return formatted data as well as gold label
        for query_input, query_label in tqdm(dataset_generator(dataset, demonstrations), total=args.num_evaluations):
            # import pdb
            # pdb.set_trace()
            #receive response from openai
            response = send_query_to_openai(query_input)
            if (response == ""):
                print("OpenAI API failed")
            temp_obj = {"label": query_label, "predict": response}
            #store the response with correct format into jsonl file
            f.write(json.dumps(temp_obj) + "\n")
