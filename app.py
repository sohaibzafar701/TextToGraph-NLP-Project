from flask import Flask, render_template, request, send_file
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import wikipedia
from pyvis.network import Network
import math
import torch

app = Flask(__name__)

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

class KB():
    def __init__(self):
        self.relations = []

    def are_relations_equal(self, r1, r2):
        return all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)

    def add_relation(self, r):
        if not self.exists_relation(r):
            self.relations.append(r)

    def print_kb(self):
        print("Entities:")
        for e in self.entities.items():
            print(f"  {e}")
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")  



##


class KB_Wiki():
    def __init__(self):
        self.entities = {}
        self.relations = []

    def are_relations_equal(self, r1, r2):
        return all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)

    def merge_relations(self, r1):
        r2 = [r for r in self.relations
              if self.are_relations_equal(r1, r)][0]
        spans_to_add = [span for span in r1["meta"]["spans"]
                        if span not in r2["meta"]["spans"]]
        r2["meta"]["spans"] += spans_to_add

    def get_wikipedia_data(self, candidate_entity):
        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary
            }
            return entity_data
        except:
            return None

    def add_entity(self, e):
        self.entities[e["title"]] = {k:v for k,v in e.items() if k != "title"}

    def add_relation(self, r):

        candidate_entities = [r["head"], r["tail"]]
        entities = [self.get_wikipedia_data(ent) for ent in candidate_entities]

        if any(ent is None for ent in entities):
            return


        for e in entities:
            self.add_entity(e)

        r["head"] = entities[0]["title"]
        r["tail"] = entities[1]["title"]

        if not self.exists_relation(r):
            self.relations.append(r)
        else:
            self.merge_relations(r)

    def print(self):
        print("Entities:")
        for e in self.entities.items():
            print(f"  {e}")
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")

##    


##

def from_text_to_kb(text, span_length=128, verbose=False):

    inputs = tokenizer([text], return_tensors="pt")

    num_tokens = len(inputs["input_ids"][0])
    if verbose:
        print(f"Input has {num_tokens} tokens")
    num_spans = math.ceil(num_tokens / span_length)
    if verbose:
        print(f"Input has {num_spans} spans")
    overlap = math.ceil((num_spans * span_length - num_tokens) /
                        max(num_spans - 1, 1))
    spans_boundaries = []
    start = 0
    for i in range(num_spans):
        spans_boundaries.append([start + span_length * i,
                                 start + span_length * (i + 1)])
        start -= overlap
    if verbose:
        print(f"Span boundaries are {spans_boundaries}")

    # transform input with spans
    tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]]
                  for boundary in spans_boundaries]
    tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]]
                    for boundary in spans_boundaries]
    inputs = {
        "input_ids": torch.stack(tensor_ids),
        "attention_mask": torch.stack(tensor_masks)
    }

    # generate relations
    num_return_sequences = 3
    gen_kwargs = {
        "max_length": 256,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": num_return_sequences
    }
    generated_tokens = model.generate(
        **inputs,
        **gen_kwargs,
    )


    decoded_preds = tokenizer.batch_decode(generated_tokens,
                                           skip_special_tokens=False)


    kb = KB()
    i = 0
    for sentence_pred in decoded_preds:
        current_span_index = i // num_return_sequences
        relations = extract_relations_from_model_output(sentence_pred)
        for relation in relations:
            relation["meta"] = {
                "spans": [spans_boundaries[current_span_index]]
            }
            kb.add_relation(relation)
        i += 1

    return kb


##

def extract_relations_from_model_output(text):
    relations = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    text_replaced = text.replace("<s>", "").replace("<pad>", "").replace("</s>", "")
    for token in text_replaced.split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        relations.append({
            'head': subject.strip(),
            'type': relation.strip(),
            'tail': object_.strip()
        })
    return relations

def save_network_html(kb, filename):
    net = Network(directed=True, width="auto", height="700px", bgcolor="#eeeeee", notebook=True)

    color_entity = "#00FF00"
    entities = set()  # Create an empty set to store unique entities
    for r in kb.relations:
        entities.add(r["head"])
        entities.add(r["tail"])

    for e in entities:
        net.add_node(e, shape="circle", color=color_entity)

    for r in kb.relations:
        net.add_edge(r["head"], r["tail"], title=r["type"], label=r["type"])

    net.repulsion(
        node_distance=200,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )
    net.set_edge_smooth('dynamic')
    net.show(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    text = request.form['text']
    option = request.form['option']

    if option == 'short_text':
        kb = KB()
        model_inputs = tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors='pt')
        generated_tokens = model.generate(**model_inputs, max_length=216, length_penalty=0, num_beams=3, num_return_sequences=3)
        decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

        for sentence_pred in decoded_preds:
            relations = extract_relations_from_model_output(sentence_pred)
            for r in relations:
                kb.add_relation(r)

        filename = "short_text_knowledge_graph.html"
        save_network_html(kb, filename)

    elif option == 'long_text':
        kb = KB()
        verbose = False
        # Tokenize the input text and split it into spans
        inputs = tokenizer([text], return_tensors="pt")
        num_tokens = len(inputs["input_ids"][0])
        span_length = 128  # Set the desired span length
        num_spans = math.ceil(num_tokens / span_length)
        overlap = math.ceil((num_spans * span_length - num_tokens) / max(num_spans - 1, 1))
        spans_boundaries = []
        start = 0
        for i in range(num_spans):
            spans_boundaries.append([start + span_length * i, start + span_length * (i + 1)])
            start -= overlap
        
        # Debugging: Print span boundaries
        if verbose:
            print(f"Span boundaries are {spans_boundaries}")

        # Transform input with spans
        tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]] for boundary in spans_boundaries]
        tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]] for boundary in spans_boundaries]
        inputs = {
            "input_ids": torch.stack(tensor_ids),
            "attention_mask": torch.stack(tensor_masks)
        }

        # Generate relations for each span
        generated_tokens = model.generate(**inputs, max_length=256, length_penalty=0, num_beams=3, num_return_sequences=3)
        decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

        # Extract relations from model output and add them to the knowledge base
        i = 0
        for sentence_pred in decoded_preds:
            current_span_index = i // 3
            relations = extract_relations_from_model_output(sentence_pred)
            for relation in relations:
                relation["meta"] = {"spans": [spans_boundaries[current_span_index]]}
                kb.add_relation(relation)
            i += 1

        # Save the knowledge base as an HTML file
        filename = "long_text_knowledge_graph.html"
        save_network_html(kb, filename)

    elif option == 'wikipedia':
        kb_wiki = KB_Wiki()
        candidate_entities = [entity.strip() for entity in text.split('.')]
        for entity in candidate_entities:
            try:
                page = wikipedia.page(entity, auto_suggest=False)
                entity_data = {
                    "title": page.title,
                    "url": page.url,
                    "summary": page.summary
                }
                kb.add_entity(entity_data)
                print(f"Added entity: {entity_data}")
            except Exception as e:
                print(f"Failed to add entity '{entity}': {str(e)}")
                continue
        # Generate knowledge base from Wikipedia entities only, no need to call from_text_to_kb again
        kb_wiki.print()
        filename = "network_wikipedia.html"
        save_network_html(kb, filename)

    return send_file(filename)

if __name__ == '__main__':
    app.run(debug=True)


