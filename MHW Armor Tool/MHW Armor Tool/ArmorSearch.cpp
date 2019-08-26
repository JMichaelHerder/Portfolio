#include "ArmorSearch.h"

// Constructor
ArmorSearch::ArmorSearch(Json::Value& const root) {
	armorJson = new Json::Value;
	this->armorJson = &root;
}

// Copy Constructor
ArmorSearch::ArmorSearch(const ArmorSearch& other) {
	armorJson = new Json::Value;
	*armorJson = *other.armorJson;
}

// Move Constructor
ArmorSearch::ArmorSearch(ArmorSearch&& other) : armorJson(other.armorJson) {
	other.armorJson = nullptr;
}

// Copy Assignment
ArmorSearch& ArmorSearch::operator=(const ArmorSearch& other) {
	if (&other == this) {
		return *this;
	}

	delete armorJson;

	armorJson = new Json::Value;
	*armorJson = *other.armorJson;

	return *this;
}

// Move Assignment
ArmorSearch& ArmorSearch::operator=(ArmorSearch&& other) {
	if (&other == this) {
		return *this;
	}

	delete armorJson;

	armorJson = other.armorJson;
	other.armorJson = nullptr;

	return *this;
}

ArmorSearch::~ArmorSearch(){
	armorJson->~Value();
}

Json::Value ArmorSearch::getJson() {
	return *armorJson;
}


/**
* Searches JSON for armors matching provided skill.
*
* @param resultList - List to populate with matching armors
* @param skillName - Name of skill to check against skills in JSON
*/
void ArmorSearch::searchBySkill(std::vector<Json::Value>& resultList, string& skillName) {
	// Checks if skillName is correct format:
	//		- Hyphens, forward-slashes, and spaces only allowed between strings of alphabetic characters
	//		- Disallows multiple spaces, hyphens, and forward-slashes
	if (std::regex_match(skillName, std::regex("^[[:alpha:]]([-/ ]?[[:alpha:]]+)*"))) {
		resultList.clear();

		// Reformats skill name to enable case-insensitive search
		for (int i = 0; i < skillName.length(); i++) {
			if (i == 0 || !isalpha(skillName.at(i - 1))) {
				skillName[i] = toupper(skillName.at(i)); // Capitalizes first letter of each word
			}
			else if (isalpha(skillName.at(i))) {
				skillName[i] = tolower(skillName.at(i)); // Makes all other characters lowercase, ignoring special characters
			}
		}

		// Use reformatted skill name to find matching armors
		for (auto const& armor : (*armorJson)["armors"]) {
			if (armor["skills"].isMember(skillName)) {
				resultList.push_back(armor);
			}
		}
	}
	else {
		std::cout << "Incorrect name format:-Only use letters and spaces.\n" << std::endl;
	}
}

/**
* Searches JSON for armors matching provided name. 
*
* @param resultList - List to populate with matching armors
* @param armorName - Name of armor to check against "name_en" field in JSON
*/
void ArmorSearch::searchByName(std::vector<Json::Value>& resultList, string& const armorName) {

}

//void searchByRank(std::vector<Json::Value>& resultList, string& const rankName);
//void searchByType(std::vector<Json::Value>& resultList, string& const typeName);