class TeamService {
    constructor() {
        this.members = [
            { id: 'usr_001', name: 'Alice Chen', email: 'alice@corp.io', role: 'Owner' },
            { id: 'usr_002', name: 'Bob Smith', email: 'bob@corp.io', role: 'Admin' },
            { id: 'usr_003', name: 'Charlie Kim', email: 'charlie@corp.io', role: 'Developer' },
        ];
    }

    listMembers() {
        return this.members;
    }

    inviteMember(email, role = 'Developer') {
        const newMember = {
            id: `usr_${Date.now()}`,
            name: email.split('@')[0],
            email,
            role,
        };
        this.members.push(newMember);
        return newMember;
    }
}

module.exports = new TeamService();
