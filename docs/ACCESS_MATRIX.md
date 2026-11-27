\# Access Matrix



| Role | Action | Expected | Observed | Evidence |

|---|---|---|---|---|

| owner | Create check | Allowed | Allowed. The Add Check button was visible on the owner dashboard, and a test check was created. | Screenshot 2026-11-27 143801.png |

| member | Create check | Allowed | Allowed. The Add Check button was visible in the member project, and the “aisha” check was created. | Screenshot 2026-11-27 144255.png |

| viewer | Create check | Denied | Allowed. The viewer project displayed the Add Check button, and the “Aisha Anjum Abbasi” check was created. | Screenshot 2026-11-27 144424.png; Screenshot 2026-11-27 144504.png |

| viewer | View checks | Allowed | Allowed. The viewer was able to access the project and view the check list. | Screenshot 2026-11-27 144424.png |

| viewer | Delete check | Denied | Allowed. The viewer was able to open the Remove Check confirmation dialog, and the check was removed. | Screenshot 2026-11-27 144453.png; Screenshot 2026-11-27 144504.png |

| member | Delete check | Allowed | Allowed. The member was able to open the Remove Check confirmation dialog for the “aisha” check, and the check was removed. | Screenshot 2026-11-27 144306.png; Screenshot 2026-11-27 144318.png |

