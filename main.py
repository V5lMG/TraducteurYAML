from deep_translator import GoogleTranslator
import ruamel.yaml

API_KEY = 'VOTRE CLE API GOOGLE'


def translate_text(text):
    try:
        # Utilisation des traductions spécifiques pour certains mots
        translations = {
            'kingdom': 'royaume',
            'ranks': 'rangs',
            'powercell': 'cellule d\'énergie',
            'extractor': 'extracteur',
            'outpost': 'avant-poste',
            'warp pad': 'plaque de téléportation',
            'regulator': 'Optimisateur',
            'siege cannon': 'Canon de siège',
            'node': 'nom brut',
            'audit logs': 'événements'
        }
        if text.strip() in translations:
            return translations[text.strip()]
        else:
            translation = GoogleTranslator(source='en', target='fr').translate(text)
            return translation
    except Exception as e:
        raise Exception(f"Erreur lors de la traduction du texte : {text}\nErreur : {e}")


def translate_yaml(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        yaml = ruamel.yaml.YAML(typ='safe')
        yaml.default_flow_style = False

        for line in f_in:
            translated_line = line

            # Vérifier si la ligne est un commentaire (commence par "#")
            if line.startswith("#"):
                translated_line = line  # Laisser la ligne inchangée
            elif ':' in line:
                key, value = line.split(':', 1)
                try:
                    translated_value = translate_text(value.strip())
                    if translated_value == value.strip():
                        # Réécrire la ligne si la traduction est identique au texte original
                        translated_line = line
                    else:
                        translated_line = f'{key}: {translated_value}\n'
                except Exception as e:
                    print(f"Erreur lors de la traduction de la ligne : {line}")
                    print(f"Erreur : {e}")
                    continue

            f_out.write(translated_line)

    print("Traduction terminée !")


input_file = 'en.yml'
output_file = 'fr.yml'

translate_yaml(input_file, output_file)
